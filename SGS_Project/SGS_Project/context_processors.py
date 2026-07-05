from .middleware import obtener_entidades_sesion
from Apps.Administracion.models import (
    Modulo,
    ModuloCategorias,
    GrupoPersona,
    AgrupacionModulos,
    AgrupacionModulosPersona,
)


def obtener_secciones_sidebar(request):
    if not request.user.is_authenticated:
        return []

    if request.user.is_superuser:
        modulos_permitidos = Modulo.objects.filter(status=True, activo=True)
    else:
        entidades = obtener_entidades_sesion()
        persona = entidades.get("persona")

        if not persona:
            return []

        grupos_persona_ids = GrupoPersona.objects.filter(
            persona=persona, status=True
        ).values_list("grupo_id", flat=True)

        grupos_modulo_ids = AgrupacionModulosPersona.objects.filter(
            grupo_persona_id__in=grupos_persona_ids, status=True
        ).values_list("grupo_modulo_id", flat=True)

        modulos_ids = AgrupacionModulos.objects.filter(
            grupo_modulo_id__in=grupos_modulo_ids, status=True
        ).values_list("modulo_id", flat=True)

        modulos_permitidos = Modulo.objects.filter(
            id__in=modulos_ids, status=True, activo=True
        )

    categorias_ids = (
        modulos_permitidos.values_list("categorias_id", flat=True).distinct()
    )

    categorias = ModuloCategorias.objects.filter(
        id__in=categorias_ids, status=True
    ).order_by("prioridad", "nombre")

    secciones = []
    # Limpiamos la ruta actual para comparar con precisión
    current_path = request.path.lower().rstrip("/")

    for categoria in categorias:
        # Ejecuta tu función original (retorna QuerySet de diccionarios)
        mods = categoria.mismodulos(modulos_permitidos)

        if mods:
            modulos_con_estado = []
            categoria_activa = False

            for modulo in mods:
                # Extraemos de forma segura tratándose de un diccionario puro
                url_raw = modulo.get("url", "") or ""
                icono_raw = modulo.get("icono") or "fa-solid fa-gears"
                nombre_raw = modulo.get("nombre", "")

                mod_url = f"/{url_raw.lower()}".rstrip("/")

                # Evaluamos si la URL actual coincide con el módulo
                is_active = (current_path == mod_url) or (
                    request.path.lower().startswith(mod_url + "/")
                )

                if is_active:
                    categoria_activa = True

                # Guardamos un diccionario idéntico para que el HTML sea feliz
                modulos_con_estado.append(
                    {
                        "url": url_raw,
                        "icono": icono_raw,
                        "nombre": nombre_raw,
                        "is_active": is_active,
                    }
                )

            secciones.append(
                {
                    "categoria": categoria,
                    "modulos": modulos_con_estado,
                    "is_active": categoria_activa,
                }
            )

    return secciones


def entidades_sesion_context(request):
    entidades = obtener_entidades_sesion()

    return {
        'persona_sesion': entidades.get('persona'),
        'usuario_sesion': entidades.get('user'),
        'secciones_sidebar': obtener_secciones_sidebar(request),
    }
