import threading

# Contenedor global seguro para hilos
_thread_locals = threading.local()


def obtener_entidades_sesion():
    return {
        'user': getattr(_thread_locals, 'user', None),
        'persona': getattr(_thread_locals, 'persona', None)
    }


class GlobalRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = None
        _thread_locals.persona = None

        if request.user and request.user.is_authenticated:
            _thread_locals.user = request.user

            try:
                from core.models import Persona
                _thread_locals.persona = Persona.objects.get(user=request.user)
            except (ImportError, Exception):
                _thread_locals.persona = None

        response = self.get_response(request)

        # Limpieza
        _thread_locals.user = None
        _thread_locals.persona = None

        return response