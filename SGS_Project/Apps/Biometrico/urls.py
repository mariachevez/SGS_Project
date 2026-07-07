from django.urls import path
from .views import *

urlpatterns = [
    path('configuracion_ingreso/', ListarConfiguracionesBiometrico.as_view(), name='listar_configuraciones'),
    path('configuracion_ingreso/crear/', CrearConfiguracionView.as_view(), name='crear_configuracion'),
    path('configuracion_ingreso/editar/<int:pk>/', EditarConfiguracionView.as_view(), name='editar_configuracion'),
    path('configuracion_ingreso/eliminar/<int:pk>/', EliminarConfiguracionView.as_view(), name='eliminar_configuracion'),
    path('ingreso_area/', ModuloMarcajeView.as_view(), name='ingreso_area'),
    path('ingreso_area/procesar/', ProcesarMarcajeView.as_view(), name='procesar_marcaje'),
]