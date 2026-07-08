from django.urls import path
from .views import *
from core.models import EliminarBase
urlpatterns = [
    
    path('solicitud/', ListadoSolicitudes.as_view(), name='listado_solicitudes'),
path('solicitud/<int:pk>/mi-respuesta/', ViewRespuestaSolicitante.as_view(), name='ver_mi_respuesta'),
    path('solicitud/crear_nueva_solicitud/', CrearSolicitud.as_view(), name='crear_nueva_solicitud'),
    path('solicitud/editar_solicitud/<int:pk>/', EditarSolicitud.as_view(), name='editar_solicitud'),
    path('solicitud/eliminar_solicitud/<int:pk>/', EliminarBase.as_view(model=Solicitudes), name='eliminar_solicitud'),
    path('director/solicitudes/', ListarSolicitudesRecibidas.as_view(), name='solicitudes_director'),
    path('director/solicitudes/<int:pk>/responder/', ResponderSolicitudView.as_view(), name='responder_solicitud'),

    path('director/solicitudes/<int:pk>/', ViewRespuestaSolicitud.as_view(), name='ver_respuesta')
]
