from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView

from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView
from ...models import *
from  ...forms import *
from core.models import EliminarBase
from core.views import AjaxExceptionMixin

class ListadoCanton(ListView):
    model = Canton
    template_name = 'Canton/index.html'
    paginate_by = 10
    context_object_name = 'cantones'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(nombre__icontains=search)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Cantones'
        return context

class CrearCanton(BaseCreateView):
    model = Canton
    form_class = CantonForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_canton')
    
    def form_valid(self, form):
        messages.success(self.request, 'Se ha guardado exitosamente')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_canton')
        return context

class EditarCanton(BaseUpdateView):
    model = Canton
    form_class = CantonForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_canton')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_canton', kwargs={'pk': self.object.pk})
        return context

class EliminarCanton(BaseDeleteView):
    model = Canton
    redirect_url = reverse_lazy('listado_canton')