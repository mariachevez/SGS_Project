from .middleware import obtener_entidades_sesion


def entidades_sesion_context(request):
    """
    Inyecta automáticamente al usuario y a la persona vinculada
    en el contexto global de cualquier template HTML del proyecto.
    """
    entidades = obtener_entidades_sesion()

    return {
        'persona_sesion': entidades['persona'],
        'usuario_sesion': entidades['user']
    }