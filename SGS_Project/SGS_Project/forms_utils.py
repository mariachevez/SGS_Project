# ==========================================
# 1. Librerías estándar de Python
# ==========================================
import logging

# ==========================================
# 2. Librerías de terceros (Django)
# ==========================================
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView, View

# ==========================================
# 3. Aplicaciones/Módulos locales del proyecto
# ==========================================
from SGS_Project.middleware import obtener_entidades_sesion

from core.views import AjaxExceptionMixin
from core.funciones import log

logger = logging.getLogger(__name__)

class BaseCreateView(AjaxExceptionMixin, CreateView):
    """Vista base de creación compatible con Modales/AJAX y tradicional."""

    def form_valid(self, form):
        self.object = form.save()
        nombre_modelo = self.model._meta.verbose_name.capitalize()
        mensaje = f"Registro de {nombre_modelo} guardado exitosamente."

        entidades = obtener_entidades_sesion()
        sesion_user = entidades['user']
        sesion_persona = entidades['persona']

        nombre_en_sesion = f'{sesion_persona.nombre_completo_minus()}' if sesion_persona else f'{sesion_user.get_full_name()}'

        # Auditoría automática en django_admin_log
        log(
            mensaje=f"{nombre_en_sesion} Creó el registro: {str(self.object)}",
            request=self.request,
            accion="add",
            objeto=self.object
        )

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get(
                'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'result': True,
                'message': mensaje,
                'url': str(self.get_success_url())
            })

        messages.success(self.request, mensaje)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        errores = {field: errors[0] for field, errors in form.errors.items()}
        mensaje_error = errores.get('__all__', "Por favor, corrija los errores en el formulario.")

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get(
                'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'result': False,
                'message': mensaje_error,
                'errors': errores
            }, status=400)

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class BaseUpdateView(AjaxExceptionMixin, UpdateView):
    """Vista base de actualización compatible con Modales/AJAX y tradicional."""

    def form_valid(self, form):
        self.object = form.save()
        nombre_modelo = self.model._meta.verbose_name.capitalize()
        mensaje = f"Registro de {nombre_modelo} actualizado exitosamente."

        entidades = obtener_entidades_sesion()
        sesion_user = entidades['user']
        sesion_persona = entidades['persona']

        nombre_en_sesion = f'{sesion_persona.nombre_completo_minus()}' if sesion_persona else f'{sesion_user.first_name} {sesion_user.last_name}'

        # Auditoría automática en django_admin_log
        log(
            mensaje=f"{nombre_en_sesion} Modificó el registro: {str(self.object)}",
            request=self.request,
            accion="chg",
            objeto=self.object
        )

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get(
                'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'result': True,
                'message': mensaje,
                'url': str(self.get_success_url())
            })

        messages.success(self.request, mensaje)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        errores = {field: errors[0] for field, errors in form.errors.items()}
        mensaje_error = errores.get('__all__', "Por favor, corrija los errores en el formulario.")

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get(
                'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'result': False,
                'message': mensaje_error,
                'errors': errores
            }, status=400)

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

class BaseDeleteView(AjaxExceptionMixin, View):
    """
    Vista base optimizada para AJAX que alterna el campo booleano 'status'
    de cualquier modelo enviada mediante un método POST.
    """
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

            entidades = obtener_entidades_sesion()
            sesion_user = entidades['user']
            sesion_persona = entidades['persona']

            nombre_en_sesion = f'{sesion_persona.nombre_completo_minus()}' if sesion_persona else f'{sesion_user.first_name} {sesion_user.last_name}'

            # Auditoría automática del cambio de estado
            log(
                mensaje=f"{nombre_en_sesion} Cambió el estado a {'ACTIVO' if objeto.status else 'INACTIVO'} del registro: {str(objeto)}",
                request=self.request,
                accion="chg",
                objeto=objeto
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get(
                    'HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({
                    'result': True,
                    'message': mensaje,
                    'url': self.get_redirect_url()
                })

            messages.success(request, mensaje)

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