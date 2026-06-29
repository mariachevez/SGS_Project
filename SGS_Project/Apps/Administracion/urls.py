from django.urls import path
from .views import *

urlpatterns = [
    
    # Persona
    path('listado_personal/', ListadoPersona.as_view(), name='listado_persona'),
    path('crear_persona/', CrearPersona.as_view(), name='crear_persona'),
    path('editar_persona/<int:pk>', EditarPersona.as_view(), name='editar_persona'),
    path('inactivar_persona/<int:pk>', InactivarPersona.as_view(), name='inactivar_persona'),
    
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
    
    # Areas
    path('listado_areas/', ListarArea.as_view(), name='listado_areas'),
    path('crear_area/', CrearArea.as_view(), name='crear_area'),
    path('editar_area/<int:pk>', EditarArea.as_view(), name='editar_area'),
    path('eliminararea/<int:pk>', EliminarArea.as_view(), name='eliminar_area'),
    path('asignar_director/<int:pk>', AsignarDirectorArea.as_view(), name='asignar_director'),
    path('adicionar_personal/<int:pk>', AgregarResponsables.as_view(), name='adicionar_personal'),
    path('buscar_persona', BuscarPersona.as_view(), name='buscar_persona'),
    path('guardar_asignacion', GuardarAsignacion.as_view(), name='guardar_asignacion'),
    
    # Búsquedas Ajax
    path('buscar_provincias/', ObtenerProvincias.as_view(), name='buscar_provincias'),
    path('buscar_cantones/', ObtenerCantones.as_view(), name='buscar_cantones'),
]