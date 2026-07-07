from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView

from core.funciones import log
from core.views import AjaxExceptionMixin
from .models import Configuracion
from .forms import ConfiguracionForm
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView, EntidadesSesionMixin


class ListarConfiguracionesBiometrico(ListView):
    model = Configuracion
    template_name = 'configuracion_index.html'
    paginate_by = 10
    context_object_name = 'configuraciones'

    def get_queryset(self):
        # Mantenemos tu filtro por defecto
        queryset = super().get_queryset().filter(status=True)
        search = self.request.GET.get('s')
        estado = self.request.GET.get('estado')

        if search:
            queryset = queryset.filter(area__nombre__icontains=search)

        if estado in ['true', 'false']:
            val_bool = estado == 'true'
            queryset = queryset.filter(activo=val_bool)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de configuraciones de acceso a las áreas'

        context['url_formcrear'] = reverse_lazy('crear_configuracion')
        context['titulo'] = 'Registrar Configuración'

        context['estado'] = self.request.GET.get('estado', '')
        return context


class CrearConfiguracionView(BaseCreateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = 'formulario.html'  # O tu plantilla base para renderizar formularios modales
    success_url = reverse_lazy('listar_configuraciones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_configuracion')
        return context


class EditarConfiguracionView(BaseUpdateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listar_configuraciones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_configuracion', kwargs={'pk': self.object.pk})
        return context


class EliminarConfiguracionView(AjaxExceptionMixin, EntidadesSesionMixin, View):
    """
    Alterna el campo 'activo' de la configuración mediante AJAX (POST).
    Cumple el flujo de la función 'eliminarAjax' de la plantilla.
    """
    model = Configuracion
    redirect_url = reverse_lazy('listar_configuraciones')

    def post(self, request, *args, **kwargs):
        objeto = get_object_or_404(self.model, pk=self.kwargs.get('pk'))

        try:
            # Alternamos el campo 'activo' en lugar de 'status'
            estado_actual = objeto.activo
            objeto.activo = not estado_actual
            objeto.save()

            nombre_objeto = self.model._meta.verbose_name.capitalize()
            accion_str = "activado" if objeto.activo else "inactivado"
            mensaje = f"Registro de {nombre_objeto} {accion_str} exitosamente."

            # Auditoría automática adaptada al cambio de estado de 'activo'
            log(
                mensaje=f"{self.nombre_en_sesion} Cambió el estado de marcaje a {'ACTIVO' if objeto.activo else 'INACTIVO'} del registro: {str(objeto)}",
                request=self.request,
                accion="edit" if objeto.activo else "del",
                objeto=objeto
            )
            messages.success(request, mensaje)

            # Respuesta para peticiones AJAX (eliminarAjax)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get(
                    'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({
                    'result': True,
                    'message': mensaje,
                    'url': self.get_redirect_url()
                })

        except Exception as e:
            mensaje_error = f"Error al cambiar el estado: {str(e)}"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get(
                    'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'result': False, 'message': mensaje_error}, status=500)
            messages.error(request, mensaje_error)

        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        if not self.redirect_url:
            raise ValueError(f"{self.__class__.__name__} debe definir 'redirect_url'.")
        return str(self.redirect_url)