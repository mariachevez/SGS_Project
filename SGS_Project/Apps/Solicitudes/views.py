from django.urls import reverse, reverse_lazy
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView
from django.views.generic import ListView
from django.db.models import Q
from SGS_Project.middleware import obtener_entidades_sesion
from .forms import *
from Apps.Notificaciones.models import *
from Apps.Administracion.models import Area


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


class ListarSolicitudesRecibidas(ListView):
    model = Solicitudes
    template_name = 'Director/index.html'
    paginate_by = 25
    context_object_name = 'listado_solicitudes'

    def get_queryset(self):
        qs = Solicitudes.objects.select_related(
            'persona',
            'area'
        ).filter(status=True).order_by('-id')

        q = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        tipo = self.request.GET.get('tipo_solicitud')
        area = self.request.GET.get('area')

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

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado solicitudes recibidas'
        context['estados'] = CoreChoices.EstadoSolicitud.choices
        context['tipos_solicitud'] = CoreChoices.TipoSolicitud.choices
        context['areas'] = Area.objects.filter(status=True).order_by('nombre')
        return context