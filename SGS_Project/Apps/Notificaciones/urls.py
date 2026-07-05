from django.urls import path
from .views import *
from core.models import EliminarBase

urlpatterns = [

    path('notificaciones/', ListadoNotificaciones.as_view(), name='listado_notificaciones'),
    path('notificaciones/leer/<int:pk>/', MarcarNotificacionLeida.as_view(), name='marcar_notificacion_leida'),
]
