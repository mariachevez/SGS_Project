import json
from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from ...models import *
from ...forms import *
from core.models import EliminarBase
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
        return context
    
class CrearArea(AjaxExceptionMixin, CreateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AreaForm
    success_url = reverse_lazy('listado_areas')
    
    def form_valid(self, form):
        messages.success(self.request, 'Guardado exitoso')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_area')
        return context
    
class EditarArea(AjaxExceptionMixin, UpdateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AreaForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_area', kwargs={'pk': self.object.pk})
        return context
    
    def form_valid(self):
        messages.success(self.request, 'Se ha editado correctamente')
        return redirect(self.get_success_url())
    
class EliminarArea(AjaxExceptionMixin, EliminarBase):
    model = Area
    success_url = reverse_lazy('listado_areas')
    
class AsignarDirectorArea(AjaxExceptionMixin, UpdateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AsignacionDirectorForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('asignar_director', kwargs={'pk': self.object.pk})
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Se ha asignado el director correctamente')
        return super().form_valid(form)

class AgregarResponsables(AjaxExceptionMixin, View):
    template_name = 'personalformulario.html'
    def get(self, request, pk):
        area = Area.objects.filter(status=True, pk=pk)
        if not area:
            return JsonResponse({'result': False, 'mensaje': 'Error al obtener el área'})
    
        return render(request, self.template_name, {'area': area})
    
    def post(self, request, pk):
        area = Area.objects.filter(status=True, pk=pk)
        if not area:
            return JsonResponse({'result': False, 'mensaje': 'No es área válido'})
        
        try:
            personas = json.loads(request.POST['personas_list'])
        except Exception as ex:
            return JsonResponse({'result': False, 'mensaje': f'{ex}'})