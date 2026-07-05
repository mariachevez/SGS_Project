from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView
from django.views.generic import ListView

from SGS_Project.middleware import obtener_entidades_sesion
from .models import *
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
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']

        return super().get_queryset().filter(status=True, persona=persona)
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Solicitudes'
        context['url_formcrear'] = reverse('crear_nueva_solicitud')
        context['titulo'] = 'Registrar Solicitud'
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

        area_inst = Area.objects.get(pk=area)
        try:
            director = area_inst.get_director()
        except ValueError as e:
            form.add_error('area', str(e))
            return self.form_invalid(form)

        Notificaciones(titulo='Se ha ingresado una nueva solicitud', 
                       descripcion=f'La descripción es la siguiente: {descripcion}',
                       destinatario=director,
                       tipo_notificacion = "M").save()
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