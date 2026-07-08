import threading
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from Apps.Administracion.models import GrupoPersona, AgrupacionModulosPersona, AgrupacionModulos, Modulo

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
                from Apps.Administracion.models import Persona
                _thread_locals.persona = Persona.objects.get(usuario=request.user)
            except (ImportError, Exception):
                _thread_locals.persona = None

        response = self.get_response(request)

        # Limpieza
        _thread_locals.user = None
        _thread_locals.persona = None

        return response


class ControlAccesoModuloMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Si no está autenticado, pasa (Django manejará el LoginRequired)
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 2. REGLA DE ORO: Si es superusuario, puede interactuar con el sistema
        if request.user.is_superuser:
            return self.get_response(request)

        # 3. Obtener el url_name de la ruta actual
        try:
            match = resolve(request.path_info)
            current_url_name = match.url_name
        except Exception:
            current_url_name = None

        if not current_url_name:
            return self.get_response(request)

        # 4. URLs de infraestructura básica exceptuadas (Evitan bucles infinitos)
        urls_publicas = ['panel_principal', 'logout', 'login', 'modulos_administracion', 'buscar_provincias', 'buscar_cantones', 'listado_notificaciones', 'mi_perfil']
        if current_url_name in urls_publicas or request.path_info.startswith('/admin/'):
            return self.get_response(request)

        # 5. BLOQUEO DINÁMICO DE ADMINISTRACIÓN (SOLO SUPERUSUARIOS)
        # Identifica palabras clave en tus 'name=' de los urlpatterns de administración
        keywords_administracion = ['modulo', 'administracion', 'agrupar', 'desagrupar']

        es_ruta_administrativa = any(key in current_url_name for key in keywords_administracion)

        # Como no es superusuario (validado en paso 2), si intenta entrar aquí se bloquea de inmediato
        if es_ruta_administrativa:
            messages.error(request, "Acceso denegado: Esta zona de configuración está reservada para Superusuarios.")
            return redirect('panel_principal')

        # 6. PROTECCIÓN DINÁMICA ABSOLUTA POR PREFIJOS (ESTILO VBF)
        try:
            persona = request.user.persona_set.filter(status=True).first()

            if not persona:
                messages.error(request, "Acceso denegado: Su usuario no tiene un perfil asignado.")
                return redirect('login')

            # Traza de grupos vinculados a la persona
            grupo_ids = GrupoPersona.objects.filter(
                persona=persona, status=True
            ).values_list('grupo_id', flat=True)

            grupo_modulo_ids = AgrupacionModulosPersona.objects.filter(
                grupo_persona_id__in=grupo_ids, status=True
            ).values_list('grupo_modulo_id', flat=True)

            modulos_permitidos_ids = AgrupacionModulos.objects.filter(
                grupo_modulo_id__in=grupo_modulo_ids, status=True
            ).values_list('modulo_id', flat=True)

            # 1. Obtenemos el path actual que pide el navegador (ej: "persona/crear")
            path_actual = request.path_info.strip('/').lower()

            # 2. Obtenemos los prefijos registrados en la BD (ej: ["persona", "grupo", "pais"])
            urls_permitidas_raw = Modulo.objects.filter(
                id__in=modulos_permitidos_ids, status=True, activo=True
            ).values_list('url', flat=True)

            # Limpiamos espacios, barras y minúsculas de la base de datos
            prefijos_permitidos = [str(url).strip('/').lower() for url in urls_permitidas_raw if url]

            # 3. VERIFICACIÓN DE PREFIJO: Comprueba si la ruta actual empieza con el prefijo permitido
            # ej: ¿"persona/crear/" empieza con "persona"? -> ¡Sí, acceso concedido!
            acceso_permitido = any(
                path_actual.startswith(prefijo) for prefijo in prefijos_permitidos if prefijo
            )

            if not acceso_permitido:
                messages.error(request,
                               f"No tienes autorización para interactuar con el módulo: /{path_actual.split('/')[0]}")
                return redirect('panel_principal')

        except Exception as e:
            messages.error(request, "Error de seguridad al procesar tus accesos de grupo.")
            return redirect('panel_principal')

        return self.get_response(request)