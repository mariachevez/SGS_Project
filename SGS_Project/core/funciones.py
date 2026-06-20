# ==========================================
# 1. Librerías estándar de Python
# ==========================================
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from user_agents import parse

def get_client_ip(request):
    """Obtiene la IP real del cliente manejando proxies o balanceadores de carga."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log(mensaje, request, accion, user=None, objeto=None):
    """
    Registra una acción en las bitácoras de django_admin_log sumando
    información de auditoría del dispositivo, IP y navegador.
    """
    try:
        # 1. Determinar el flag de la acción
        if accion == "del":
            logaction = DELETION
        elif accion == "add":
            logaction = ADDITION
        else:
            logaction = CHANGE

        # 2. Extraer información del entorno del usuario si hay un request válido
        if request:
            user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
            user_ip = get_client_ip(request)
            user_device = user_agent.device.family
            user_browser = user_agent.browser.family
            user_os_type = user_agent.os.family
            user_os_version = user_agent.os.version_string

            if user_agent.is_pc:
                user_device_type = 'PC'
            elif user_agent.is_mobile:
                user_device_type = 'Teléfono Móvil'
            elif user_agent.is_tablet:
                user_device_type = 'Tablet'
            else:
                user_device_type = 'Otros'

            # Formateamos el mensaje inyectando la metadata de auditoría
            mensaje = (
                f"{mensaje} | IP: {user_ip} | "
                f"Dispositivo: {user_device_type}/{user_device} | "
                f"Navegador/OS: {user_browser}/{user_os_type}-{user_os_version}"
            )

        # 3. Obtener ContentType y IDs si pasaste un objeto del modelo (Mejora opcional pero recomendada)
        content_type_id = None
        object_id = None
        object_repr = ''

        if objeto:
            from django.contrib.contenttypes.models import ContentType
            content_type_id = ContentType.objects.get_for_model(objeto).id
            object_id = objeto.pk
            object_repr = str(objeto)[:200]  # El admin requiere una representación en texto del registro

        # 4. Determinar qué usuario realiza la acción
        usuario_id = user.id if user else (request.user.id if request and request.user.is_authenticated else None)

        if usuario_id:
            LogEntry.objects.log_action(
                user_id=usuario_id,
                content_type_id=content_type_id,
                object_id=object_id,
                object_repr=object_repr,
                action_flag=logaction,
                change_message=str(mensaje)  # Cambiado unicode() por str() para Python 3
            )

    except Exception as ex:
        # Usamos un print o idealmente el logger para saber si falla la auditoría sin tumbar el sistema
        print(f"Error al guardar log de auditoría: {ex}")

def validar_cedula(cedula):
    if len(cedula) != 10:
            raise Exception("Cédula con longitud incorrecta")
        
    if not cedula.isdigit():
        raise Exception("Por favor ingrese solo números")
    
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        raise Exception("El código de provincia no es válido (01–24).")
    
    tercer_digito = int(cedula[2])
    
    if tercer_digito >= 6:
        raise Exception("El tercer dígito no corresponde a una cédula de persona natural.")
    
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i, coef in enumerate(coeficientes):
        producto = int(cedula[i]) * coef
        if producto >= 10:
            producto -= 9
        total += producto

    digito_verificador = int(cedula[9])
    resultado = (10 - (total % 10)) % 10

    if resultado != digito_verificador:
        raise Exception("La cédula ingresada no es válida.")

    return cedula