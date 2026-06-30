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


class ListadoGrupos(ListView):
    model = Grupo
    template_name = 'Grupo/index.html'
    paginate_by = 10
    context_object_name = 'grupos'

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=True)
        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(nombre__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Grupos'
        context['url_formcrear'] = reverse('crear_grupo')
        context['titulo'] = 'Registrar Grupo'
        return context


class CrearGrupo(BaseCreateView):
    model = Grupo
    form_class = GrupoForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_grupos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_grupo')
        return context


class EditarGrupo(BaseUpdateView):
    model = Grupo
    form_class = GrupoForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listado_grupos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_grupo', kwargs={'pk': self.object.pk})
        return context


class EliminarGrupo(BaseDeleteView):
    model = Grupo
    redirect_url = reverse_lazy('listado_grupos')