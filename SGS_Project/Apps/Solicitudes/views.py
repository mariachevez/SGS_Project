from django.urls import reverse, reverse_lazy
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, EntidadesSesionMixin
from django.views.generic import ListView, UpdateView, DetailView
from django.db.models import Q
from SGS_Project.middleware import obtener_entidades_sesion
from core.funciones import log
from core.views import AjaxExceptionMixin
from .forms import *
from Apps.Notificaciones.models import *
from Apps.Administracion.models import Area
from ..Notificaciones.utils import generar_notificacion


# Create your views here.

class ListadoSolicitudes(ListView):
    model = Solicitudes
    template_name = 'Solicitudes/index.html'
    paginate_by = 25
    context_object_name = 'solicitudes'

    def get_queryset(self):
        queryset = super().get_queryset()
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']

        queryset = queryset.filter(status=True, persona=persona)

        estado = self.request.GET.get('estado', '').strip()
        if estado:
            queryset = queryset.filter(estado_solicitud=estado)

        area = self.request.GET.get('area', '').strip()
        if area:
            queryset = queryset.filter(area_id=area)

        return queryset

    def get_context_data(self, **kwargs):
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Solicitudes'
        context['url_formcrear'] = reverse('crear_nueva_solicitud')
        context['titulo'] = 'Registrar Solicitud'
        context['areas'] = Solicitudes.objects.filter(status=True, persona=persona).values_list('area_id',
                                                                                                'area__nombre').order_by(
            'area_id').distinct(
            'area_id')
        context['estados'] = CoreChoices.EstadoSolicitud.choices
        return context


class CrearSolicitud(BaseCreateView):
    model = Solicitudes
    form_class = NuevaSolicitudForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_solicitudes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_nueva_solicitud')
        return context

    def form_valid(self, form):
        descripcion = self.request.POST.get('descripcion')
        area = self.request.POST.get('area')
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']
        if not persona:
            form.add_error(None, 'No existe una persona asociada a la sesión actual.')
            return self.form_invalid(form)
        form.instance.persona = persona
        area_inst = Area.objects.get(pk=area)
        try:
            director = area_inst.get_director()
        except ValueError as e:
            form.add_error('area', str(e))
            return self.form_invalid(form)

        Notificaciones(titulo='Se ha ingresado una nueva solicitud',
                       descripcion=f'La descripción es la siguiente: {descripcion}',
                       destinatario=director,
                       tipo_notificacion="M").save()
        return super().form_valid(form)


class EditarSolicitud(BaseUpdateView):
    model = Solicitudes
    form_class = NuevaSolicitudForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_solicitudes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_solicitud', kwargs={'pk': self.object.pk})
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)


class ListarSolicitudesRecibidas(EntidadesSesionMixin, ListView):
    model = Solicitudes
    template_name = 'Director/index.html'
    paginate_by = 25
    context_object_name = 'listado_solicitudes'

    def get_queryset(self):
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']
        if persona:
            qs = Solicitudes.objects.select_related(
                'persona',
                'area'
            ).filter(status=True, area__director=self.persona_sesion).order_by('-id')
        else:
            qs = Solicitudes.objects.filter(status=True).order_by('-id')

        q = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        tipo = self.request.GET.get('tipo_solicitud')
        area = self.request.GET.get('area')
        solicitante = self.request.GET.get('solicitante')

        if q:
            qs = qs.filter(
                Q(persona__nombres__icontains=q) |
                Q(persona__apellido1__icontains=q) |
                Q(persona__apellido2__icontains=q) |
                Q(descripcion__icontains=q)
            )

        if estado:
            qs = qs.filter(estado_solicitud=estado)

        if tipo:
            qs = qs.filter(tipo_solicitud=tipo)

        if area:
            qs = qs.filter(area_id=area)

        if solicitante:
            qs = qs.filter(persona_id=solicitante)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado solicitudes recibidas'
        context['estados'] = CoreChoices.EstadoSolicitud.choices
        context['tipos_solicitud'] = CoreChoices.TipoSolicitud.choices
        if self.persona_sesion:
            qs = Solicitudes.objects.select_related(
                'persona',
                'area'
            ).filter(status=True, area__director=self.persona_sesion).order_by('persona_id').distinct('persona_id')
        else:
            qs = Solicitudes.objects.filter(status=True).order_by('persona_id').distinct('persona_id')
        context['solicitantes'] = qs
        context['areas'] = Area.objects.filter(status=True).order_by('nombre')
        solicitante_id = self.request.GET.get('solicitante')
        context['solicitante_id'] = int(solicitante_id) if solicitante_id and solicitante_id.isdigit() else ''

        return context


class ResponderSolicitudView(BaseUpdateView):
    model = Solicitudes
    form_class = ResponderSolicitudForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('solicitudes_director')

    def dispatch(self, request, *args, **kwargs):
        # Ejecuta el dispatch base para inyectar self.persona_sesion
        response = super().dispatch(request, *args, **kwargs)
        solicitud = self.get_object()
        # Control de seguridad explícito para el Director
        # if not self.persona_sesion or solicitud.area.director != self.persona_sesion:
        #     raise PermissionDenied("No tienes permisos para responder solicitudes de esta área.")

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('responder_solicitud', kwargs={'pk': self.object.pk})
        return context

    def form_valid(self, form):
        form.instance.fecha_resolucion = timezone.now()

        solicitud = self.get_object()
        estado_nuevo = form.cleaned_data.get('estado_solicitud')

        if solicitud.persona:
            generar_notificacion('Su solicitud ha sido atendida',
                                 f'El Director del área ha cambiado el estado de su solicitud a: {estado_nuevo}.',
                                 destinatario=solicitud.persona,
                                 tipo_notificacion='M')
        return super().form_valid(form)

class ViewRespuestaSolicitud(EntidadesSesionMixin, AjaxExceptionMixin, DetailView):
    model = Solicitudes
    template_name = 'Director/ver_respuesta.html'
    context_object_name = 'solicitud'

class ViewRespuestaSolicitante(EntidadesSesionMixin, AjaxExceptionMixin, DetailView):
    model = Solicitudes
    template_name = 'Solicitudes/ver_respuesta.html'
    context_object_name = 'solicitud'

    def get_queryset(self):
        # El solicitante solo puede ver el detalle de sus propias solicitudes
        return Solicitudes.objects.filter(persona=self.persona_sesion)