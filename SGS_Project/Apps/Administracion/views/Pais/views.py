from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView

from SGS_Project.forms_utils import BaseCreateView
from ...models import *
from ...forms import *
from core.models import EliminarBase
from core.views import AjaxExceptionMixin

class ListadoPaises(ListView):
    model = Pais
    template_name = 'Pais/index.html'
    paginate_by = 10
    context_object_name = 'paises'
    
    def get_queryset(self):
        return Pais.objects.filter(status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Paises'
        return context


# PAÍS
class CrearPais(BaseCreateView):
    model = Pais
    form_class = PaisForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_pais')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_pais')
        return context

class EditarPais(AjaxExceptionMixin, UpdateView):
    model = Pais
    form_class = PaisForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_pais')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_pais', kwargs={'pk': self.object.pk})
        return context

class EliminarPais(AjaxExceptionMixin, EliminarBase):
    model = Pais
    success_url = reverse_lazy('listado_pais')