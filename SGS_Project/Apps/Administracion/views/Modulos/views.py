from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.list import BaseListView

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
        context['ret'] = reverse('modulos_administracion')
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


class ListadoGruposModulos(ListView):
    model = GrupoModulo
    template_name = 'Modulos/grupos_modulos_index.html'
    paginate_by = 25
    context_object_name = 'grupos_modulos'

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=True)
        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(nombre__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de grupos de modulos'
        context['ret'] = reverse('modulos_administracion')
        context['url_formcrear'] = reverse('crear_grupo_modulo')
        context['titulo'] = 'Registrar Grupo de Modulos'
        context['s'] = self.request.GET.get('s')
        return context

class CrearGrupoModulo(BaseCreateView):
    model = GrupoModulo
    form_class = GrupoModuloForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_grupos_modulos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_grupo_modulo')
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)

class EditarGrupoModulo(BaseUpdateView):
    model = GrupoModulo
    form_class = GrupoModuloForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_grupos_modulos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_grupo_modulo', kwargs={'pk': self.object.pk})
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)

class InactivarGrupoModulo(BaseDeleteView):
    model = GrupoModulo
    redirect_url = reverse_lazy('listado_grupos_modulos')

class ListadoModulos(ListView):
    model = Modulo
    template_name = 'Modulos/modulos_index.html'
    paginate_by = 25
    context_object_name = 'modulos'

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=True)
        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(nombre__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de modulos'
        context['ret'] = reverse('modulos_administracion')
        context['url_formcrear'] = reverse('crear_modulo')
        context['titulo'] = 'Registrar Modulo'
        context['s'] = self.request.GET.get('s')
        return context

class CrearModulo(BaseCreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_modulos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_modulo')
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)

class EditarModulo(BaseUpdateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_modulos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_modulo', kwargs={'pk': self.object.pk})
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)

class InactivarModulo(BaseDeleteView):
    model = Modulo
    redirect_url = reverse_lazy('listado_modulos')

class ListadoAgrupacionModulosporGrupo(ListView):
    model = AgrupacionModulos
    template_name = 'Modulos/agrupacionmodulosporgrupo_index.html'
    paginate_by = 25
    context_object_name = 'modulos'

    def get_queryset(self):
        grupo_modulo_id = self.kwargs['grupo_modulo_id']
        search = self.request.GET.get('s')
        queryset = super().get_queryset().select_related('modulo').filter(
            status=True, grupo_modulo_id=grupo_modulo_id
        )
        if search:
            queryset = queryset.filter(modulo__nombre__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de modulos que pertenecen al grupo.'
        context['ret'] = reverse('modulos_administracion')
        context['url_formcrear'] = reverse('agrupar_modulo', kwargs={'grupo_modulo_id': self.kwargs['grupo_modulo_id']})
        context['titulo'] = 'Agrupar Modulo'
        context['s'] = self.request.GET.get('s')
        return context


class AgruparModulo(BaseCreateView):
    model = AgrupacionModulos
    form_class = AgruparModuloForm
    template_name = 'formulario.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['grupo_modulo_id'] = self.kwargs['grupo_modulo_id']
        return kwargs

    def get_success_url(self):
        return reverse('listado_agrupacionmodulosporgrupo', kwargs={'grupo_modulo_id': self.kwargs['grupo_modulo_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('agrupar_modulo', kwargs={'grupo_modulo_id': self.kwargs['grupo_modulo_id']})
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)


class DesagruparModulo(BaseDeleteView):
    """Se usa desde el lado Grupo: vuelve al listado de módulos de ese grupo."""
    model = AgrupacionModulos

    def get_redirect_url(self):
        agrupacion = get_object_or_404(AgrupacionModulos, pk=self.kwargs.get('pk'))
        return reverse('listado_agrupacionmodulosporgrupo', kwargs={'grupo_modulo_id': agrupacion.grupo_modulo_id})


class ListadoAgrupacionModulosGrupos(ListView):
    model = AgrupacionModulos
    template_name = 'Modulos/agrupaciongrupospormodulo_index.html'
    paginate_by = 25
    context_object_name = 'grupos'

    def get_queryset(self):
        modulo_id = self.kwargs['modulo_id']
        search = self.request.GET.get('s')
        queryset = super().get_queryset().select_related('grupo_modulo').filter(
            status=True, modulo_id=modulo_id
        )
        if search:
            queryset = queryset.filter(grupo_modulo__nombre__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de grupos asociados a este módulo.'
        context['url_formcrear'] = reverse('agrupar_grupo_modulo', kwargs={'modulo_id': self.kwargs['modulo_id']})
        context['titulo'] = 'Asociar Grupo'
        context['s'] = self.request.GET.get('s')
        return context


class AgruparModuloGrupo(BaseCreateView):
    """Se usa desde el lado Módulo: el modulo_id viene fijo, se elige el grupo_modulo."""
    model = AgrupacionModulos
    form_class = AgruparModuloForm
    template_name = 'formulario.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['modulo_id'] = self.kwargs['modulo_id']
        return kwargs

    def get_success_url(self):
        return reverse('listado_agrupacionmodulosgrupos', kwargs={'modulo_id': self.kwargs['modulo_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('agrupar_grupo_modulo', kwargs={'modulo_id': self.kwargs['modulo_id']})
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)


class DesagruparGrupoModulo(BaseDeleteView):
    """Se usa desde el lado Módulo: vuelve al listado de grupos de ese módulo."""
    model = AgrupacionModulos

    def get_redirect_url(self):
        agrupacion = get_object_or_404(AgrupacionModulos, pk=self.kwargs.get('pk'))
        return reverse('listado_agrupacionmodulosgrupos', kwargs={'modulo_id': agrupacion.modulo_id})