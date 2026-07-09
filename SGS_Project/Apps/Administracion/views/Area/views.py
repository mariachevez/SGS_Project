import json

from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView

from Apps.Biometrico.models import CabRegistro
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView, EntidadesSesionMixin
from SGS_Project.middleware import obtener_entidades_sesion
from core.funciones import log
from core.reports.reportes_excel import DjangoReportThreadPool
from ...forms import *
from core.views import AjaxExceptionMixin
from Apps.Notificaciones.utils import generar_notificacion

class ListarArea(ListView):
    model = Area
    template_name = 'Area/index.html'
    paginate_by = 10
    context_object_name = 'areas'
    
    def get_queryset(self):
        return Area.objects.filter(status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Áreas'
        context['url_formcrear'] = reverse('crear_area')
        context['titulo'] = 'Registrar Área'
        return context
    
class CrearArea(BaseCreateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AreaForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_area')
        return context
    
class EditarArea(BaseUpdateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AreaForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_area', kwargs={'pk': self.object.pk})
        return context
    
class EliminarArea(BaseDeleteView):
    model = Area
    redirect_url = reverse_lazy('listado_areas')
    
class AsignarDirectorArea(BaseUpdateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AsignacionDirectorForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('asignar_director', kwargs={'pk': self.object.pk})
        return context

class ListarPlantillaArea(ListView):
    model = AreaPersona
    template_name = 'Area/plantilla_area_index.html'
    paginate_by = 25
    context_object_name = 'personal'

    def get_queryset(self):
        area_id = self.kwargs['area_id']
        search = self.request.GET.get('s')
        queryset = super().get_queryset().select_related('area').filter(
            status=True, area_id=area_id
        )
        if search:
            queryset = queryset.filter(persona__nombres__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['area'] = area = Area.objects.get(pk=self.kwargs['area_id'])
        context['nombre_tabla'] = f'Listado de personas que pertenecen al area de "{area.nombre.capitalize()}".'
        context['ret'] = reverse('listado_areas')
        context['url_formcrear'] = reverse('adicionar_personal', kwargs={'area_id': self.kwargs['area_id']})
        context['titulo'] = 'Agregar personal a la plantilla.'
        context['s'] = self.request.GET.get('s')
        return context


class AgregarResponsables(AjaxExceptionMixin, View):
    template_name = 'Area/personalformulario.html'

    def dispatch(self, request, *args, **kwargs):
        entidades = obtener_entidades_sesion()
        self.usuario_sesion = entidades.get('user')
        self.persona_sesion = entidades.get('persona')

        if self.persona_sesion:
            self.nombre_en_sesion = self.persona_sesion.nombre_completo_minus()
        elif self.usuario_sesion:
            self.nombre_en_sesion = self.usuario_sesion.get_full_name()
        else:
            self.nombre_en_sesion = "Sistema"

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, area_id):
        area = Area.objects.filter(status=True, pk=area_id).first()
        if not area:
            return JsonResponse({'result': False, 'mensaje': 'Error al obtener el área'}, status=404)

        # Filtro inicial para cargar el select con gente libre y activa
        personas = Persona.objects.filter(status=True)
        return render(request, self.template_name, {'area': area, 'personas': personas})

    def post(self, request, area_id):
        area = Area.objects.filter(status=True, pk=area_id).first()
        if not area:
            return JsonResponse({'result': False, 'mensaje': 'No es un área válida'}, status=400)

        persona_id = request.POST.get('persona_id')
        if not persona_id:
            return JsonResponse({'result': False, 'mensaje': 'Falta seleccionar al trabajador'}, status=400)

        try:
            if AreaPersona.objects.filter(persona_id=persona_id, status=True).exists():
                return JsonResponse({'result': False, 'mensaje': 'Esta persona ya está actualmente asignada a un área'})

            # Guardado Real en la Base de Datos
            nueva_asignacion = AreaPersona(area_id=area.id, persona_id=persona_id, status=True)
            nueva_asignacion.save()

            director = nueva_asignacion.area.get_director()

            generar_notificacion('Se ha asignado una persona a su área',
                                 f'La persona es: {nueva_asignacion.persona.nombre_completo_minus()}',
                                 director, CoreChoices.TipoNotificacion.BAJA)

            # Devolver los que quedan disponibles
            personas_restantes = Persona.objects.filter(status=True)
            personas_list = [{'id': p.id, 'nombres': p.nombre_completo_minus()} for p in personas_restantes]

            log(
                mensaje=f"{self.nombre_en_sesion} Registró a la persona {nueva_asignacion.persona.nombre_completo_minus()} en el área: {nueva_asignacion.area.nombre.capitalize()}",
                request=self.request,
                accion="add",
                objeto=nueva_asignacion
            )

            return JsonResponse({
                'result': True,
                'personas': personas_list,
                'mensaje': 'Se ha guardado con éxito el registro'
            })
        except Exception as ex:
            return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'}, status=500)


class BuscarPersonalArea(View):
    def get(self, request):
        persona_id = request.GET.get('id')
        if not persona_id:
            return JsonResponse({'result': False, 'mensaje': 'Por favor, seleccione una persona'}, status=400)

        # ARREGLADO: Buscamos directo por ID y status activo. No le metas validaciones inversas de área aquí.
        persona = Persona.objects.filter(pk=persona_id, status=True).first()

        if not persona:
            return JsonResponse({
                'result': False,
                'mensaje': 'La persona no se encuentra activa o no existe.'
            }, status=404)

        foto_url = persona.get_foto()
        foto_completa = request.build_absolute_uri(foto_url) if foto_url else "/static/images/default-avatar.png"

        return JsonResponse({
            'result': True,
            'id': persona.pk,
            'foto': foto_completa,
            'nombres': persona.nombre_completo_minus() if callable(persona.nombre_completo_minus) else persona.nombre_completo_minus,
            'identificacion': persona.identificacion
        })
    
class EliminarPersonalArea(BaseDeleteView):
    model = AreaPersona

    def get_redirect_url(self):
        pk = self.kwargs.get('pk')
        objeto = get_object_or_404(self.model, pk=pk)
        area_id = objeto.area_id
        return reverse('listado_plantilla_area', args=[area_id])


class PlantillaPersonalDirectorListView(EntidadesSesionMixin, ListView):
    """
    Vista para que los directores consulten los trabajadores de las áreas que tienen a su cargo.
    Hereda de EntidadesSesionMixin para obtener automáticamente `self.persona_sesion`.
    """
    model = AreaPersona
    template_name = "Area/mi_area_index.html"  # Ajusta tu ruta de template
    context_object_name = "trabajadores_area"
    paginate_by = 15  # Opcional: para integrarse con tu paginador_base.html

    def get_queryset(self):
        # 1. Obtener las áreas donde la persona en sesión es el Director
        if not self.persona_sesion:
            return AreaPersona.objects.none()

        areas_dirigidas = Area.objects.filter(director=self.persona_sesion)

        # 2. Traer todos los AreaPersona asociados a esas áreas con select_related para optimizar queries (SQL Join)
        queryset = AreaPersona.objects.filter(area__in=areas_dirigidas, status=True).select_related('persona', 'area')

        # 3. Aplicar Filtro por Buscador (Nombre, apellido, identificación o email de la persona)
        search_query = self.request.GET.get('s', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(persona__first_name__icontains=search_query) |
                Q(persona__last_name__icontains=search_query) |
                Q(persona__cedula__icontains=search_query) |  # Ajusta según el campo único que uses
                Q(persona__email__icontains=search_query)
            )

        # 4. Aplicar Filtro por Estado (Asumiendo que AreaPersona o Persona tienen el atributo 'status')
        status_query = self.request.GET.get('estado', '').strip()
        if status_query:
            # Ejemplo filtrando por el estado de la relación. Si deseas filtrar por el de la Persona: persona__status
            is_active = status_query.lower() in ['true', '1', 'activo']
            queryset = queryset.filter(status=is_active)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = "Listado del Personal"
        context['placeholder'] = "Buscar por nombre, cédula o correo..."

        # Obtenemos el área que diriges (o la primera si tienes varias)
        if self.persona_sesion:
            context['mi_area'] = Area.objects.filter(director=self.persona_sesion).first()

        return context

class ReporteAreasView(View):
    """
    Vista Basada en Clases (VBC) para lanzar el reporte de personas.
    Redirige a la URL actual y muestra un mensaje flash de Django.
    """

    def get(self, request, *args, **kwargs):
        filtros = request.GET.dict()
        filtros['status'] = True
        reportador = DjangoReportThreadPool(usuario_solicitante=request.user)
        reportador.reporte_areas_thread(**filtros)
        messages.success(request, 'Tu reporte se está procesando. Te llegará una notificación cuando esté listo para descargar.')
        url_actual = request.META.get('HTTP_REFERER')
        if url_actual:
            return redirect(url_actual)
        else:
            return redirect('panel_principal')

class ReportePlantillaAreasView(View):
    """
    Vista Basada en Clases (VBC) para lanzar el reporte de personas.
    Redirige a la URL actual y muestra un mensaje flash de Django.
    """

    def get(self, request, *args, **kwargs):
        filtros = request.GET.dict()

        # .pop() saca el 'area_id' del diccionario y te lo da. Así ya no se duplica en **filtros
        area_id = filtros.pop('area_id', None)

        filtros['status'] = True

        reportador = DjangoReportThreadPool(usuario_solicitante=request.user)
        reportador.reporte_plantilla_area_thread(area_id, **filtros)

        messages.success(request,
                         'Tu reporte se está procesando. Te llegará una notificación cuando esté listo para descargar.')

        url_actual = request.META.get('HTTP_REFERER')
        if url_actual:
            return redirect(url_actual)
        return redirect('panel_principal')

class ListadoMarcajesPersonalView(EntidadesSesionMixin, ListView):
    model = CabRegistro
    template_name = 'Area/ver_registros_ingresos_salidas.html'  # Define tu ruta de template
    paginate_by = 25
    context_object_name = 'registros'

    def dispatch(self, request, *args, **kwargs):
        # Obtenemos el registro de la plantilla de área usando la PK enviada por el botón
        self.area_persona = get_object_or_404(AreaPersona, pk=self.kwargs.get('pk'), status=True)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Filtramos estrictamente las transacciones que correspondan a esa persona y en esa área específica
        return CabRegistro.objects.filter(
            status=True,
            persona=self.area_persona.persona,
            area=self.area_persona.area
        ).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Devolvemos el área y la persona al contexto tal como lo solicitaste
        context['area'] = self.area_persona.area
        context['persona'] = self.area_persona.persona
        context['nombre_tabla'] = f"Historial de Accesos - {self.area_persona.persona.nombre_completo_minus()}"
        return context


class VerDetalleMarcajeModalView(EntidadesSesionMixin, AjaxExceptionMixin, DetailView):
    model = CabRegistro
    template_name = 'Area/detalle_ingreso_salida.html'  # El fragmento HTML que cargará en el modal
    context_object_name = 'cabecera'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenemos el primer detalle vinculado al registro biométrico (donde se aloja la foto y los booleanos de EPP)
        context['detalle'] = self.object.detalles.filter(status=True).first()
        return context