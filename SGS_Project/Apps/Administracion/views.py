from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from .models import *
from .forms import *

class EliminarBase(View):
    model = None

    def post(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=pk, status=True)
        messages.success(request, 'Registro eliminado con éxito')
        obj.delete_status()
        return JsonResponse({
            'success': True,
            'message': 'Registro eliminado correctamente'
        })
    
    
class ListadoPersona(ListView):
    model = Persona
    template_name = 'index.html'
    paginate_by = 10
    context_object_name = 'personas'

    def get_queryset(self):
        return Persona.objects.filter(status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado del Personal'
        return context
    
class CrearPersona(CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_persona')
    
    def form_valid(self, form):
        messages.success(self.request, 'Se ha guardado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_persona')
        # context['cancelar'] = reverse('listado_persona')
        return context

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

class CrearPais(CreateView):
    model = Pais
    form_class = PaisForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_pais')
    
    def form_valid(self, form):
        messages.success(self.request, 'Se ha guardado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_pais')
        return context

class EditarPais(UpdateView):
    model = Pais
    form_class = PaisForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_pais')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_pais', kwargs={'pk': self.object.pk})
        return context
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.save(usuario_id = self.request.user.id)
        messages.success(self.request, 'Se ha editado correctamente')
        return redirect(self.get_success_url())

class EliminarPais(EliminarBase):
    model = Pais
    success_url = reverse_lazy('listado_pais')
    