from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.db.models import Q
from SGS_Project.forms_utils import AjaxExceptionMixin, EntidadesSesionMixin
from core.funciones import log
from .models import Notificaciones
from SGS_Project.middleware import obtener_entidades_sesion

class ListadoNotificaciones(ListView):
    model = Notificaciones
    template_name = 'Notificaciones/index.html'
    paginate_by = 10
    context_object_name = 'notificaciones'

    def get_queryset(self):
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']

        if persona:
            queryset = super().get_queryset().filter(
                status=True,
                destinatario=persona
            )
        else:
            queryset = super().get_queryset().filter(status=True)

        search = self.request.GET.get('s', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()

        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(destinatario__nombres__icontains=search) |
                Q(destinatario__apellido1__icontains=search) |
                Q(destinatario__apellido2__icontains=search)
            )

        if estado != '':
            queryset = queryset.filter(estado_notificacion=estado == '1')

        if tipo:
            queryset = queryset.filter(tipo_notificacion=tipo)

        return queryset.order_by('destinatario', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Notificaciones'

        query_params = self.request.GET.copy()

        if 'page' in query_params:
            del query_params['page']

            # 3. Creamos el string url_vars:
            # Si hay filtros, devuelve "&s=texto&estado=1", si no, devuelve ""
        context['url_vars'] = f"&{query_params.urlencode()}" if query_params else ""

        context['s'] = self.request.GET.get('s', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['tipo'] = self.request.GET.get('tipo', '')

        context['tipos_notificacion'] = Notificaciones._meta.get_field(
            'tipo_notificacion'
        ).choices

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


class MarcarTodasLeidas(AjaxExceptionMixin, EntidadesSesionMixin, View):
    def post(self, request, *args, **kwargs):
        entidades = obtener_entidades_sesion()
        persona = entidades['persona']

        try:
            # Si hay una persona en sesión, lee solo las suyas. Si es superuser sin persona asignada, lee todas.
            if persona:
                notificaciones_sin_leer = Notificaciones.objects.filter(
                    destinatario=persona,
                    estado_notificacion=False,
                    status=True
                )
            else:
                notificaciones_sin_leer = Notificaciones.objects.filter(
                    estado_notificacion=False,
                    status=True
                )

            cantidad = notificaciones_sin_leer.count()
            if cantidad > 0:
                notificaciones_sin_leer.update(estado_notificacion=True)

                log(
                    mensaje=f"{self.nombre_en_sesion} marcó todas sus ({cantidad}) notificaciones como leídas.",
                    request=self.request,
                    accion="edit"
                )
                messages.success(request, f"Se marcaron {cantidad} notificaciones como leídas.")
            else:
                messages.info(request, "No tienes notificaciones pendientes por leer.")

        except Exception as e:
            messages.error(request, f"Error al actualizar las notificaciones: {str(e)}")

        return redirect('/notificaciones/')