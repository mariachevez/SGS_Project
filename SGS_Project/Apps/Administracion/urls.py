from django.urls import path
from .views import *
from .views.Grupo.views import ListadoGrupos, CrearGrupo, EditarGrupo, EliminarGrupo
from .views.Modulos.views import *

urlpatterns = [

    # Persona
    path('listado_personal/', ListadoPersona.as_view(), name='listado_persona'),
    path('crear_persona/', CrearPersona.as_view(), name='crear_persona'),
    path('editar_persona/<int:pk>', EditarPersona.as_view(), name='editar_persona'),
    path('inactivar_persona/<int:pk>', InactivarPersona.as_view(), name='inactivar_persona'),

    #Grupos
    path('listado_grupos/', ListadoGrupos.as_view(), name='listado_grupos'),
    path('crear_grupo/', CrearGrupo.as_view(), name='crear_grupo'),
    path('editar_grupo/<int:pk>', EditarGrupo.as_view(), name='editar_grupo'),
    path('eliminar_grupo/<int:pk>', EliminarGrupo.as_view(), name='eliminar_grupo'),

    #Enrolar Grupos
    path('listado_grupos_persona/<int:persona_id>/', ListadoGrupoPersona.as_view(), name='listado_grupos_persona'),
    path('enrolar_persona/<int:persona_id>/', CrearGrupoPersona.as_view(), name='enrolar_persona'),
    path('eliminar_grupo_persona/<int:pk>/', InactivarGrupoPersona.as_view(), name='eliminar_grupo_persona'),


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

    # Administracion
    path('modulos_administracion/', TemplateView.as_view(template_name='Administracion/index.html'), name='modulos_administracion'),
    path('listado_modulo_categorias', ListadoModuloCategorias.as_view(), name='listado_modulo_categorias'),
    path('crear_modulo_categoria', CrearModuloCategoria.as_view(), name='crear_modulo_categoria'),
    path('editar_modulo_categoria/<int:pk>/', EditarModuloCategoria.as_view(), name='editar_modulo_categoria'),
    path('inactivar_modulo_categoria/<int:pk>/', InactivarModuloCategoria.as_view(), name='inactivar_modulo_categoria'),

    path('listado_grupos_modulos', ListadoGruposModulos.as_view(), name='listado_grupos_modulos'),
    path('crear_grupo_modulo', CrearGrupoModulo.as_view(), name='crear_grupo_modulo'),
    path('editar_grupo_modulo/<int:pk>/', EditarGrupoModulo.as_view(), name='editar_grupo_modulo'),
    path('inactivar_grupo_modulo/<int:pk>/', InactivarGrupoModulo.as_view(), name='inactivar_grupo_modulo'),

    path('listado_modulos', ListadoModulos.as_view(), name='listado_modulos'),
    path('crear_modulo', CrearModulo.as_view(), name='crear_modulo'),
    path('editar_modulo/<int:pk>/', EditarModulo.as_view(), name='editar_modulo'),
    path('inactivar_modulo/<int:pk>/', InactivarModulo.as_view(), name='inactivar_modulo'),

    path('listado_agrupacionmodulosporgrupo/<int:grupo_modulo_id>', ListadoAgrupacionModulosporGrupo.as_view(),name='listado_agrupacionmodulosporgrupo'),
    path('agrupar_modulo/<int:grupo_modulo_id>', AgruparModulo.as_view(), name='agrupar_modulo'),
    path('desagrupar_modulo/<int:pk>', DesagruparModulo.as_view(), name='desagrupar_modulo'),

    path('listado_agrupacionmodulosgrupos/<int:modulo_id>', ListadoAgrupacionModulosGrupos.as_view(),name='listado_agrupacionmodulosgrupos'),
    path('agrupar_grupo_modulo/<int:modulo_id>', AgruparModuloGrupo.as_view(), name='agrupar_grupo_modulo'),
    path('desagrupar_grupo_modulo/<int:pk>', DesagruparGrupoModulo.as_view(), name='desagrupar_grupo_modulo'),

    path('listado_agrupacion_modulos_persona', ListadoAgrupacionModulosPersona.as_view(), name='listado_agrupacion_modulos_persona'),
    path('crear_agrupacion_modulos_persona', CrearAgrupacionModulosPersona.as_view(), name='crear_agrupacion_modulos_persona'),
    path('editar_agrupacion_modulos_persona/<int:pk>/', EditarAgrupacionModulosPersona.as_view(), name='editar_agrupacion_modulos_persona'),
    path('inactivar_agrupacion_modulos_persona/<int:pk>/', InactivarAgrupacionModulosPersona.as_view(), name='inactivar_agrupacion_modulos_persona'),

    # Búsquedas Ajax
    path('buscar_provincias/', ObtenerProvincias.as_view(), name='buscar_provincias'),
    path('buscar_cantones/', ObtenerCantones.as_view(), name='buscar_cantones'),
]