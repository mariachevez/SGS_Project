from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from .models import *
from .forms import *
from core.models import EliminarBase
from core.funciones import validar_cedula
    
    
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
        persona_form = form.save(commit=False)
        cedula = persona_form.cleaned_data.get('cedula')
        try:
            validar_cedula(cedula)
        except Exception as ex:
            return self.form_invalid(form)
        messages.success(self.request, 'Se ha guardado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_persona')
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


# PAÍS
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



# PROVINCIA
class ListadoProvincia(ListView):
    model = Provincia
    template_name = 'Provincia/index.html'
    paginate_by = 10
    context_object_name = 'provincias'
    
    def get_queryset(self):
        return Provincia.objects.filter(status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Provincias'
        return context
    
class CrearProvincia(CreateView):
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
    
class EditarProvincia(UpdateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_provincia')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_provincia', kwargs={'pk': self.object.pk})
        return context
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.save(usuario_id = self.request.user.id)
        messages.success(self.request, 'Se ha editado correctamente el registro')
        return redirect(self.get_success_url())    

class EliminarProvincia(EliminarBase):
    model = Provincia
    success_url = reverse_lazy('listado_provincia')


# CANTON
class ListadoCanton(ListView):
    model = Canton
    template_name = 'Canton/index.html'
    paginate_by = 10
    context_object_name = 'cantones'
    
    def get_queryset(self):
        return Canton.objects.filter(status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Cantones'
        return context

class CrearCanton(CreateView):
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

class EditarCanton(UpdateView):
    model = Canton
    form_class = CantonForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_canton')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_canton', kwargs={'pk': self.object.pk})
        return context
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.save(usuario_id = self.request.user.id)
        messages.success(self.request, 'Se ha editado correctamente')
        return redirect(self.get_success_url())

class EliminarCanton(EliminarBase):
    model = Canton
    success_url = reverse_lazy('listado_canton')

