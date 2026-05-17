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

]