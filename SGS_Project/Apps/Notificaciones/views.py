from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from SGS_Project.forms_utils import AjaxExceptionMixin, EntidadesSesionMixin
from core.funciones import log
from .models import Notificaciones
from SGS_Project.middleware import obtener_entidades_sesion

# Create your views here.

class ListadoNotificaciones(ListView):
    model = Notificaciones
    template_name = 'Notificaciones/index.html'
    paginate_by = 10
    context_object_name = 'notificaciones'

    def get_queryset(self):
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']
        if persona:
            queryset = super().get_queryset().filter(status=True, destinatario=persona).order_by('-estado_notificacion', '-id')
        else:
            queryset = super().get_queryset().filter(status=True).order_by('-estado_notificacion', '-id')

        search = self.request.GET.get('s')

        if search:
            queryset = queryset.filter(titulo__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Notificaciones'
        return context


class LeerNotificacion(AjaxExceptionMixin, EntidadesSesionMixin, View):
    model = None  # Se define en la subclase
    redirect_url = None  # Se define en la subclase (usado como fallback tradicional)

    def post(self, request, *args, **kwargs):
        objeto = get_object_or_404(self.model, pk=self.kwargs.get('pk'))

        if not hasattr(objeto, 'status'):
            mensaje_error = f"El modelo {self.model.__name__} no cuenta con el campo 'status'."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get(
                    'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'result': False, 'message': mensaje_error}, status=400)
            messages.error(request, mensaje_error)
            return redirect(self.get_redirect_url())

        try:
            estado_actual = objeto.status
            objeto.status = not estado_actual
            objeto.save()

            nombre_objeto = self.model._meta.verbose_name.capitalize()
            accion_str = "activado" if objeto.status else "inactivado"
            mensaje = f"Registro de {nombre_objeto} {accion_str} exitosamente."

            # Auditoría automática del cambio de estado
            log(
                mensaje=f"{self.nombre_en_sesion} Cambió el estado a {'ACTIVO' if objeto.status else 'INACTIVO'} del registro: {str(objeto)}",
                request=self.request,
                accion="chg",
                objeto=objeto
            )
            messages.success(request, mensaje)

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


# ==========================================
# NUEVA VISTA: MARCAR COMO LEÍDA Y REDIRIGIR
# ==========================================
class MarcarNotificacionLeida(AjaxExceptionMixin, EntidadesSesionMixin, View):
    model = Notificaciones

    # Aquí puedes cambiar la cadena por tu ruta o utilizar un reverse('url_name')
    redirect_url = '/notificaciones/'

    def get(self, request, *args, **kwargs):
        """Manejador GET para que funcione directo al hacer clic en el enlace del Navbar"""
        notificacion = get_object_or_404(self.model, pk=self.kwargs.get('pk'))

        try:
            # Forzamos a que pase a leído (True)
            if not notificacion.estado_notificacion:
                notificacion.estado_notificacion = True
                notificacion.save()

                # Registro en la tabla de auditoría (opcional)
                log(
                    mensaje=f"{self.nombre_en_sesion} leyó la notificación: {notificacion.descripcion[:50]}...",
                    request=self.request,
                    accion="edit",
                    objeto=notificacion
                )

        except Exception as e:
            messages.error(request, f"Error al procesar la notificación: {str(e)}")

        # Redirige de forma tradicional al listado final
        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        return str(self.redirect_url)