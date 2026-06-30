from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView

from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView
from ...models import *
from ...forms import *
from core.models import EliminarBase
from core.views import AjaxExceptionMixin


class ListadoProvincia(ListView):
    model = Provincia
    template_name = 'Provincia/index.html'
    paginate_by = 10
    context_object_name = 'provincias'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(nombre__icontains=search)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Provincias'
        return context
    
class CrearProvincia(BaseCreateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_provincia')
    
    def form_valid(self, form):
        messages.success(self.request, 'Se ha guardado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_provincia')
        return context
    
class EditarProvincia(BaseUpdateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_provincia')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_provincia', kwargs={'pk': self.object.pk})
        return context

class EliminarProvincia(BaseDeleteView):
    model = Provincia
    redirect_url = reverse_lazy('listado_provincia')
