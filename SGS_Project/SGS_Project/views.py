from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView

from Apps.Administracion.forms import EditarPerfilForm, CambiarFotoForm
from Apps.Administracion.models import *
from SGS_Project.forms_utils import BaseUpdateView
from SGS_Project.middleware import obtener_entidades_sesion


class PanelPrincipal(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Regla para Superusuarios: Acceso irrestricto a todo lo que esté activo
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            modulos_permitidos = Modulo.objects.filter(status=True, activo=True)
            categorias_ids = modulos_permitidos.values_list('categorias_id', flat=True).distinct()
            categorias = ModuloCategorias.objects.filter(id__in=categorias_ids, status=True).order_by('prioridad',
                                                                                                      'nombre')

            secciones = []
            for categoria in categorias:
                # Obtenemos los módulos directamente como diccionarios compatibles con tu método
                mods = categoria.mismodulos(modulos_permitidos)
                if mods:
                    secciones.append({'categoria': categoria, 'modulos': mods})

            context['secciones'] = secciones
            return context

        # Flujo regular por Grupos y Personas
        entidades = obtener_entidades_sesion()  # Tu función segura por hilos
        persona = entidades['persona']

        if not persona:
            context['secciones'] = []
            return context

        # 1. Persona -> GrupoPersona (Saca grupos de la persona)
        grupos_persona_ids = GrupoPersona.objects.filter(
            persona=persona, status=True
        ).values_list('grupo_id', flat=True)

        # 2. Grupo -> AgrupacionModulosPersona (Empata con el grupo de módulos)
        grupos_modulo_ids = AgrupacionModulosPersona.objects.filter(
            grupo_persona_id__in=grupos_persona_ids, status=True
        ).values_list('grupo_modulo_id', flat=True)

        # 3. GrupoModulo -> AgrupacionModulos (Saca los módulos asignados)
        modulos_ids = AgrupacionModulos.objects.filter(
            grupo_modulo_id__in=grupos_modulo_ids, status=True
        ).values_list('modulo_id', flat=True)

        # 4. Filtro final de Módulos Activos
        modulos_permitidos = Modulo.objects.filter(
            id__in=modulos_ids, status=True, activo=True
        )

        # 5. Obtener categorías de estos módulos
        categorias_ids = modulos_permitidos.values_list('categorias_id', flat=True).distinct()
        categorias = ModuloCategorias.objects.filter(
            id__in=categorias_ids, status=True
        ).order_by('prioridad', 'nombre')

        secciones = []
        for categoria in categorias:
            # Usamos tu método nativo pasándole la lista de módulos permitidos
            mods = categoria.mismodulos(modulos_permitidos)
            if mods:
                secciones.append({'categoria': categoria, 'modulos': mods})

        context['secciones'] = secciones
        return context

class MiPerfilView(TemplateView):
    template_name = 'mi_perfil.html'  # Ajusta la ruta a donde guardes tu html

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtenemos la persona vinculada al usuario logueado
        # Usamos .first() por si el ForeignKey te devuelve un QuerySet
        persona = Persona.objects.filter(usuario=self.request.user).first()

        context['persona'] = persona
        context['titulo'] = 'Mi Perfil'
        context['nombre_tabla'] = 'Perfil de Usuario'
        return context


class EditarPerfilView(BaseUpdateView):
    model = Persona
    form_class = EditarPerfilForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('mi_perfil')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_perfil')
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Persona, usuario=self.request.user)


    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)


class CambiarFotoView(BaseUpdateView):
    model = Persona
    form_class = CambiarFotoForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('mi_perfil')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('cambiar_foto')
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Persona, usuario=self.request.user)

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)