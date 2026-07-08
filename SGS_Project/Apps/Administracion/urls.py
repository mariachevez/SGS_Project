from django.urls import path
from .views import *
from .views.Grupo.views import ListadoGrupos, CrearGrupo, EditarGrupo, EliminarGrupo
from .views.Modulos.views import *

urlpatterns = [

    # ==========================================
    # MÓDULO: PERSONA (En BD registrarás: personal)
    # ==========================================
    path('personal', ListadoPersona.as_view(), name='listado_persona'),
    path('personal/crear/', CrearPersona.as_view(), name='crear_persona'),
    path('personal/editar/<int:pk>/', EditarPersona.as_view(), name='editar_persona'),
    path('personal/inactivar/<int:pk>/', InactivarPersona.as_view(), name='inactivar_persona'),

    # ==========================================
    # MÓDULO: GRUPOS (En BD registrarás: grupo)
    # ==========================================
    path('grupo', ListadoGrupos.as_view(), name='listado_grupos'),
    path('grupo/crear/', CrearGrupo.as_view(), name='crear_grupo'),
    path('grupo/editar/<int:pk>/', EditarGrupo.as_view(), name='editar_grupo'),
    path('grupo/eliminar/<int:pk>/', EliminarGrupo.as_view(), name='eliminar_grupo'),

    # Enrolar Grupos (Dependen del módulo grupo o persona, se protegen bajo 'grupo')
    path('grupo/listado_persona/<int:persona_id>/', ListadoGrupoPersona.as_view(), name='listado_grupos_persona'),
    path('grupo/enrolar_persona/<int:persona_id>/', CrearGrupoPersona.as_view(), name='enrolar_persona'),
    path('grupo/eliminar_persona/<int:pk>/', InactivarGrupoPersona.as_view(), name='eliminar_grupo_persona'),

    # ==========================================
    # MÓDULO: PAIS (En BD registrarás: pais)
    # ==========================================
    path('pais', ListadoPaises.as_view(), name='listado_pais'),
    path('pais/crear/', CrearPais.as_view(), name='crear_pais'),
    path('pais/actualizar/<int:pk>/', EditarPais.as_view(), name='editar_pais'),
    path('pais/eliminar/<int:pk>/', EliminarBase.as_view(model=Pais), name='eliminar_pais'),

    # ==========================================
    # MÓDULO: PROVINCIA (En BD registrarás: provincia)
    # ==========================================
    path('provincia', ListadoProvincia.as_view(), name='listado_provincia'),
    path('provincia/crear/', CrearProvincia.as_view(), name='crear_provincia'),
    path('provincia/editar/<int:pk>/', EditarProvincia.as_view(), name='editar_provincia'),
    path('provincia/eliminar/<int:pk>/', EliminarProvincia.as_view(), name='eliminar_provincia'),

    # ==========================================
    # MÓDULO: CANTON (En BD registrarás: canton)
    # ==========================================
    path('canton', ListadoCanton.as_view(), name='listado_canton'),
    path('canton/crear/', CrearCanton.as_view(), name='crear_canton'),
    path('canton/editar/<int:pk>/', EditarCanton.as_view(), name='editar_canton'),
    path('canton/eliminar/<int:pk>/', EliminarCanton.as_view(), name='eliminar_canton'),

    # ==========================================
    # MÓDULO: AREAS (En BD registrarás: areas)
    # ==========================================
    path('areas', ListarArea.as_view(), name='listado_areas'),
    path('areas/crear/', CrearArea.as_view(), name='crear_area'),
    path('areas/editar/<int:pk>/', EditarArea.as_view(), name='editar_area'),
    path('areas/eliminar/<int:pk>/', EliminarArea.as_view(), name='eliminar_area'),
    path('areas/asignar_director/<int:pk>/', AsignarDirectorArea.as_view(), name='asignar_director'),
    path('areas/adicionar_personal/<int:area_id>/', AgregarResponsables.as_view(), name='adicionar_personal'),
    path('areas/buscar_personal_area/', BuscarPersonalArea.as_view(), name='buscar_persona_area'),
    path('areas/listado_plantilla_area/<int:area_id>', ListarPlantillaArea.as_view(), name='listado_plantilla_area'),
    path('areas/eliminar_personal/<int:pk>/', EliminarPersonalArea.as_view(), name='eliminar_personal_area'),
    path('mi_area', PlantillaPersonalDirectorListView.as_view(), name='mi_area'),

    # ==========================================
    # MÓDULO: ADMINISTRACION (En BD registrarás: administracion)
    # ==========================================
    path('administracion/panel/', TemplateView.as_view(template_name='Administracion/index.html'),
         name='modulos_administracion'),
    path('administracion/listado_modulo_categorias/', ListadoModuloCategorias.as_view(),
         name='listado_modulo_categorias'),
    path('administracion/crear_modulo_categoria/', CrearModuloCategoria.as_view(), name='crear_modulo_categoria'),
    path('administracion/editar_modulo_categoria/<int:pk>/', EditarModuloCategoria.as_view(),
         name='editar_modulo_categoria'),
    path('administracion/inactivar_modulo_categoria/<int:pk>/', InactivarModuloCategoria.as_view(),
         name='inactivar_modulo_categoria'),

    path('administracion/listado_grupos_modulos/', ListadoGruposModulos.as_view(), name='listado_grupos_modulos'),
    path('administracion/crear_grupo_modulo/', CrearGrupoModulo.as_view(), name='crear_grupo_modulo'),
    path('administracion/editar_grupo_modulo/<int:pk>/', EditarGrupoModulo.as_view(), name='editar_grupo_modulo'),
    path('administracion/inactivar_grupo_modulo/<int:pk>/', InactivarGrupoModulo.as_view(),
         name='inactivar_grupo_modulo'),

    path('administracion/listado_modulos/', ListadoModulos.as_view(), name='listado_modulos'),
    path('administracion/crear_modulo/', CrearModulo.as_view(), name='crear_modulo'),
    path('administracion/editar_modulo/<int:pk>/', EditarModulo.as_view(), name='editar_modulo'),
    path('administracion/inactivar_modulo/<int:pk>/', InactivarModulo.as_view(), name='inactivar_modulo'),

    path('administracion/listado_agrupacionmodulosporgrupo/<int:grupo_modulo_id>/',
         ListadoAgrupacionModulosporGrupo.as_view(), name='listado_agrupacionmodulosporgrupo'),
    path('administracion/agrupar_modulo/<int:grupo_modulo_id>/', AgruparModulo.as_view(), name='agrupar_modulo'),
    path('administracion/desagrupar_modulo/<int:pk>/', DesagruparModulo.as_view(), name='desagrupar_modulo'),

    path('administracion/listado_agrupacionmodulosgrupos/<int:modulo_id>/', ListadoAgrupacionModulosGrupos.as_view(),
         name='listado_agrupacionmodulosgrupos'),
    path('administracion/agrupar_grupo_modulo/<int:modulo_id>/', AgruparModuloGrupo.as_view(),
         name='agrupar_grupo_modulo'),
    path('administracion/desagrupar_grupo_modulo/<int:pk>/', DesagruparGrupoModulo.as_view(),
         name='desagrupar_grupo_modulo'),

    path('administracion/listado_agrupacion_modulos_persona/', ListadoAgrupacionModulosPersona.as_view(),
         name='listado_agrupacion_modulos_persona'),
    path('administracion/crear_agrupacion_modulos_persona/', CrearAgrupacionModulosPersona.as_view(),
         name='crear_agrupacion_modulos_persona'),
    path('administracion/editar_agrupacion_modulos_persona/<int:pk>/', EditarAgrupacionModulosPersona.as_view(),
         name='editar_agrupacion_modulos_persona'),
    path('administracion/inactivar_agrupacion_modulos_persona/<int:pk>/', InactivarAgrupacionModulosPersona.as_view(),
         name='inactivar_agrupacion_modulos_persona'),

    # ==========================================
    # BÚSQUEDAS AJAX (Públicas o globales)
    # ==========================================
    path('buscar_provincias/', ObtenerProvincias.as_view(), name='buscar_provincias'),
    path('buscar_cantones/', ObtenerCantones.as_view(), name='buscar_cantones'),
    path('buscar_personas/', BuscarPersonasView.as_view(), name='buscar_personas'),
]