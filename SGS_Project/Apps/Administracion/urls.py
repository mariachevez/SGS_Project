from django.urls import path
from .views import *


urlpatterns = [
    
    # Persona
    path('listado_personal/', ListadoPersona.as_view(), name='listado_persona'),
    path('crear_persona/', CrearPersona.as_view(), name='crear_persona'),
    
    # Pais
    path('listado_pais/', ListadoPaises.as_view(), name='listado_pais'),
    path('listado_paises/', CrearPais.as_view(), name='crear_pais'),
    path('acualizar_pais/<int:pk>/', EditarPais.as_view(), name='editar_pais'),
    path('eliminar_pais/<int:pk>/', EliminarPais.as_view(), name='eliminar_pais'),

    # Provincia
    path('listado_provincia/', ListadoProvincia.as_view(), name='listado_provincia'),
    path('crear_provincia/', CrearProvincia.as_view(), name='crear_provincia'),
    path('editar_provincia/<int:pk>', EditarProvincia.as_view(), name='editar_provincia'),
    path('eliminar_provincia/<int:pk>', EliminarProvincia.as_view(), name='eliminar_provincia'),
    
    # Canton
    path('listado_canton/', ListadoCanton.as_view(), name='listado_canton'),
    path('crear_canton/', CrearCanton.as_view(), name='crear_canton'),
    path('editar_canton/<int:pk>', EditarCanton.as_view(), name='editar_canton'),
    path('eliminar_canton/<int:pk>', EliminarCanton.as_view(), name='eliminar_canton'),
    
]