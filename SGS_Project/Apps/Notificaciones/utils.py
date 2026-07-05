from .models import Notificaciones
from core.models import CoreChoices

def generar_notificacion(titulo, descripcion, destinatario, tipo_notificacion=CoreChoices.TipoNotificacion.ALTA):
    eNoti = Notificaciones()
    eNoti.titulo = titulo
    eNoti.descripcion = descripcion
    eNoti.tipo_notificacion = tipo_notificacion
    eNoti.destinatario = destinatario
    eNoti.save()