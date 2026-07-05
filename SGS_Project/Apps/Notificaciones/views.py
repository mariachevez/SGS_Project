from django.shortcuts import render
from django.views.generic import ListView
from .models import Notificaciones
from SGS_Project.middleware import obtener_entidades_sesion

# Create your views here.

class ListadoNotificaciones(ListView):
    model = Notificaciones
    template_name = 'Notificaciones/index.html'
    paginate_by = 10
    context_object_name = 'notificaciones'

    def get_queryset(self):
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']
        if persona:
            queryset = super().get_queryset().filter(status=True, destinatario=persona).order_by('-estado_notificacion', '-id')
        else:
            queryset = super().get_queryset().filter(status=True).order_by('-estado_notificacion', '-id')

        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(titulo__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Notificaciones'
        return context

