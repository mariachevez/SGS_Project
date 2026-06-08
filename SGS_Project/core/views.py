from django.shortcuts import render
from django.http import JsonResponse

class AjaxExceptionMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
            if hasattr(response, 'render'):
                response.render()

            return response
        except Exception as ex:
            return JsonResponse({
                'result': False,
                'message': f'Ocurrió un error: {ex}',
            }, status=500)
# Create your views here.
