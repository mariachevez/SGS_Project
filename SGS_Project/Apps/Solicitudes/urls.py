from django.urls import path
from .views import *

urlpatterns = [
    path('listado_solicitudes/', ListadoSolicitudes.as_view(), name='listado_solicitudes'),
    path('crear_nueva_solicitud/', CrearSolicitud.as_view(), name='crear_nueva_solicitud')
]
