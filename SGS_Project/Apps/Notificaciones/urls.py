from django.urls import path
from .views import *
from core.models import EliminarBase

urlpatterns = [

    path('notificaciones/', ListadoNotificaciones.as_view(), name='listado_notificaciones'),
]
