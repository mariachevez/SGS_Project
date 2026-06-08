from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
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
        return Canton.objects.filter(status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Cantones'
        return context

class CrearCanton(AjaxExceptionMixin, CreateView):
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

class EditarCanton(AjaxExceptionMixin, UpdateView):
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

class EliminarCanton(AjaxExceptionMixin, EliminarBase):
    model = Canton
    success_url = reverse_lazy('listado_canton')