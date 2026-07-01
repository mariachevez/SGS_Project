from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView

from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView
from ...models import *
from ...forms import *
from core.models import EliminarBase
from core.views import AjaxExceptionMixin


class ListadoModuloCategorias(ListView):
    model = ModuloCategorias
    template_name = 'Modulos/categorias_index.html'
    paginate_by = 25
    context_object_name = 'categorias'

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(nombre__icontains=search)

        return queryset.order_by('prioridad', 'nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Categorías'
        context['url_formcrear'] = reverse('crear_modulo_categoria')
        context['titulo'] = 'Registrar Categoría'
        context['s'] = self.request.GET.get('s')
        context['estado'] = self.request.GET.get('estado')
        return context


class CrearModuloCategoria(BaseCreateView):
    model = ModuloCategorias
    form_class = ModuloCategoriasForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_modulo_categorias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_modulo_categoria')
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)


class EditarModuloCategoria(BaseUpdateView):
    model = ModuloCategorias
    form_class = ModuloCategoriasForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_modulo_categorias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_modulo_categoria', kwargs={'pk': self.object.pk})
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)


class InactivarModuloCategoria(BaseDeleteView):
    model = ModuloCategorias
    redirect_url = reverse_lazy('listado_modulo_categorias')