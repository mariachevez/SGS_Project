from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django import forms
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView, View, TemplateView
import logging

logger = logging.getLogger(__name__)


class AjaxExceptionMixin:
    """Atrapa errores inesperados en el servidor y responde en JSON para AJAX."""

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
            if hasattr(response, 'render'):
                response.render()
            return response
        except Exception as ex:
            logger.exception("Error interno en el servidor interceptado por el Mixin.")
            return JsonResponse({
                'result': False,
                'message': f'Ocurrió un error interno: {str(ex)}',
            }, status=500)
