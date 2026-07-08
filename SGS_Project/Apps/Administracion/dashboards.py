from django.views.generic import TemplateView
from django.db.models import Count, Q
import json

from Apps.Solicitudes.models import Solicitudes
from Apps.Administracion.models import Persona, Area, Provincia, Canton


class DashboardView(TemplateView):
    template_name = 'Dashboards/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        area_sol_id = self.request.GET.get('area_sol')
        estado_sol = self.request.GET.get('estado_sol')
        tipo_sol = self.request.GET.get('tipo_sol')

        provincia_per_id = self.request.GET.get('provincia_per')
        canton_per_id = self.request.GET.get('canton_per')
        sexo_per = self.request.GET.get('sexo_per')

        qs_solicitudes = Solicitudes.objects.filter(status=True)

        if area_sol_id:
            qs_solicitudes = qs_solicitudes.filter(area_id=area_sol_id)
        if estado_sol:
            qs_solicitudes = qs_solicitudes.filter(estado_solicitud=estado_sol)
        if tipo_sol:
            qs_solicitudes = qs_solicitudes.filter(tipo_solicitud=tipo_sol)

        qs_personas = Persona.objects.filter(status=True)

        if provincia_per_id:
            qs_personas = qs_personas.filter(provincia_id=provincia_per_id)
        if canton_per_id:
            qs_personas = qs_personas.filter(canton_id=canton_per_id)
        if sexo_per:
            qs_personas = qs_personas.filter(sexo=sexo_per)

        # ---- Solicitudes por área, desglosadas por estado ----
        solicitudes_area = qs_solicitudes.filter(
            area__isnull=False
        ).values(
            'area__nombre'
        ).annotate(
            total=Count('id'),
            pendientes=Count('id', filter=Q(estado_solicitud='P')),
            aprobados=Count('id', filter=Q(estado_solicitud='A')),
            rechazados=Count('id', filter=Q(estado_solicitud='R')),
        ).order_by('-total')

        context['areas_labels'] = json.dumps([x['area__nombre'] for x in solicitudes_area])
        context['pendientes_data'] = json.dumps([x['pendientes'] for x in solicitudes_area])
        context['aprobados_data'] = json.dumps([x['aprobados'] for x in solicitudes_area])
        context['rechazados_data'] = json.dumps([x['rechazados'] for x in solicitudes_area])

        # ---- Personal por provincia (sin cambios) ----
        personal_provincia = qs_personas.filter(
            provincia__isnull=False
        ).values(
            'provincia__nombre'
        ).annotate(
            total=Count('id'),
            masculino=Count('id', filter=Q(sexo='M')),
            femenino=Count('id', filter=Q(sexo='F')),
        ).order_by('-total')

        context['provincias_labels'] = json.dumps([x['provincia__nombre'] for x in personal_provincia])
        context['masculino_data'] = json.dumps([x['masculino'] for x in personal_provincia])
        context['femenino_data'] = json.dumps([x['femenino'] for x in personal_provincia])

        context['areas'] = Area.objects.filter(status=True).order_by('nombre')
        context['provincias'] = Provincia.objects.filter(status=True).order_by('nombre')
        context['cantones'] = Canton.objects.filter(status=True).order_by('nombre')
        context['kpi_total_solicitudes'] = qs_solicitudes.count()

        context['kpi_pendientes'] = qs_solicitudes.filter(
            estado_solicitud='P'
        ).count()

        context['kpi_aprobadas'] = qs_solicitudes.filter(
            estado_solicitud='A'
        ).count()

        context['kpi_rechazadas'] = qs_solicitudes.filter(
            estado_solicitud='R'
        ).count()
        context['area_sol_id'] = area_sol_id
        context['estado_sol'] = estado_sol
        context['tipo_sol'] = tipo_sol
        context['provincia_per_id'] = provincia_per_id
        context['canton_per_id'] = canton_per_id
        context['sexo_per'] = sexo_per
        context['kpi_total_personal'] = qs_personas.count()

        context['kpi_masculino'] = qs_personas.filter(
            sexo='M'
        ).count()

        context['kpi_femenino'] = qs_personas.filter(
            sexo='F'
        ).count()

        context['kpi_provincias'] = qs_personas.exclude(
            provincia__isnull=True
        ).values(
            'provincia'
        ).distinct().count()

        return context
