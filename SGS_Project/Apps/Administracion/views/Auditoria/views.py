from django.views.generic import ListView
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from Apps.Administracion.models import Persona  # Asegúrate de importar tu modelo
from SGS_Project.forms_utils import BasePaginadaListView


class AuditoriaPersonaListView(BasePaginadaListView):
    model = LogEntry
    template_name = 'Auditoria/auditoria_personas.html'
    context_object_name = 'logs'

    def get_queryset(self):
        qs = LogEntry.objects.select_related('user').order_by('-action_time')

        # 1. Filtrado por Persona (Usuario Autor)
        persona_id = self.request.GET.get('persona_id')
        if persona_id:
            try:
                persona = Persona.objects.get(pk=persona_id)
                if persona.usuario_id:
                    qs = qs.filter(user_id=persona.usuario_id)
                else:
                    qs = qs.none()
            except Persona.DoesNotExist:
                pass

        # 2. NUEVO: Filtrado por Estado de la acción
        estado = self.request.GET.get('estado')
        if estado:
            if estado == 'add':
                qs = qs.filter(action_flag=ADDITION)  # Filtra flag 1
            elif estado == 'edit':
                qs = qs.filter(action_flag=CHANGE)    # Filtra flag 2
            elif estado == 'del':
                qs = qs.filter(action_flag=DELETION)  # Filtra flag 3

        # 3. Buscador general de texto
        search_query = self.request.GET.get('s')
        if search_query:
            qs = qs.filter(change_message__icontains=search_query)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['nombre_tabla'] = 'Auditoría de Usuarios'
        context['titulo'] = 'Auditoría'
        context['placeholder'] = 'Buscar en los logs...'

        context['personas'] = Persona.objects.filter(
            usuario__isnull=False
        ).order_by('apellido1', 'apellido2', 'nombres')

        # Pasamos ambos estados limpios al contexto para mantener la selección activa
        context['persona_id'] = self.request.GET.get('persona_id', '')
        context['estado'] = self.request.GET.get('estado', '')

        return context