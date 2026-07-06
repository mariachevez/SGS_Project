import json
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView

from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView
from SGS_Project.middleware import obtener_entidades_sesion
from core.funciones import log
from ...forms import *
from core.views import AjaxExceptionMixin

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
        area = Area.objects.get(pk=self.kwargs['area_id'])
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

            # Devolver los que quedan disponibles
            personas_restantes = Persona.objects.filter(status=True, areas_trabajo__isnull=True, areas_dirigidas__isnull=True)
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
        
class ViewModulosAdministracion(TemplateView):
    pass