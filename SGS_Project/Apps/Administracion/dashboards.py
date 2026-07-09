from django.db.models.functions import TruncDate, ExtractHour
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.http import JsonResponse
import json

from Apps.Biometrico.models import CabRegistro
from Apps.Solicitudes.models import Solicitudes
from Apps.Administracion.models import Persona, Area, Provincia, Canton


class DashboardSolicitudesView(TemplateView):
    template_name = 'Dashboards/solicitudes_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        area_sol_id = self.request.GET.get('area_sol')
        estado_sol = self.request.GET.get('estado_sol')
        tipo_sol = self.request.GET.get('tipo_sol')

        qs_solicitudes = Solicitudes.objects.filter(status=True)

        if area_sol_id:
            qs_solicitudes = qs_solicitudes.filter(area_id=area_sol_id)
        if estado_sol:
            qs_solicitudes = qs_solicitudes.filter(estado_solicitud=estado_sol)
        if tipo_sol:
            qs_solicitudes = qs_solicitudes.filter(tipo_solicitud=tipo_sol)

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

        context['areas'] = Area.objects.filter(status=True).order_by('nombre')

        context['kpi_total_solicitudes'] = qs_solicitudes.count()
        context['kpi_pendientes'] = qs_solicitudes.filter(estado_solicitud='P').count()
        context['kpi_aprobadas'] = qs_solicitudes.filter(estado_solicitud='A').count()
        context['kpi_rechazadas'] = qs_solicitudes.filter(estado_solicitud='R').count()

        context['area_sol_id'] = area_sol_id
        context['estado_sol'] = estado_sol
        context['tipo_sol'] = tipo_sol

        return context


class DashboardPersonalView(TemplateView):
    template_name = 'Dashboards/personal_index.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('action') == 'buscar_cantones':
            provincia_id = request.GET.get('provincia_id')

            cantones = Canton.objects.filter(
                status=True,
                provincia_id=provincia_id
            ).order_by('nombre').values('id', 'nombre')

            return JsonResponse({
                'result': True,
                'cantones': list(cantones)
            })

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        provincia_per_id = self.request.GET.get('provincia_per')
        canton_per_id = self.request.GET.get('canton_per')
        sexo_per = self.request.GET.get('sexo_per')

        qs_personas = Persona.objects.filter(status=True)

        if provincia_per_id:
            qs_personas = qs_personas.filter(provincia_id=provincia_per_id)
        if canton_per_id:
            qs_personas = qs_personas.filter(canton_id=canton_per_id)
        if sexo_per:
            qs_personas = qs_personas.filter(sexo=sexo_per)

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

        context['provincias'] = Provincia.objects.filter(
            status=True,
            pais__nombre__icontains='ECUADOR'
        ).order_by('nombre')

        context['cantones'] = Canton.objects.none()
        if provincia_per_id:
            context['cantones'] = Canton.objects.filter(
                status=True,
                provincia_id=provincia_per_id
            ).order_by('nombre')

        context['kpi_total_personal'] = qs_personas.count()
        context['kpi_masculino'] = qs_personas.filter(sexo='M').count()
        context['kpi_femenino'] = qs_personas.filter(sexo='F').count()
        context['kpi_provincias'] = qs_personas.exclude(
            provincia__isnull=True
        ).values('provincia').distinct().count()

        context['provincia_per_id'] = provincia_per_id
        context['canton_per_id'] = canton_per_id
        context['sexo_per'] = sexo_per

        return context


class DashboardConcurrenciaView(TemplateView):
    template_name = 'Dashboards/acceso_area_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        area_id = self.request.GET.get('area')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')

        qs_ingresos = CabRegistro.objects.filter(status=True)

        if area_id:
            qs_ingresos = qs_ingresos.filter(area_id=area_id)

        if fecha_desde:
            qs_ingresos = qs_ingresos.filter(fecha_creacion__date__gte=fecha_desde)

        if fecha_hasta:
            qs_ingresos = qs_ingresos.filter(fecha_creacion__date__lte=fecha_hasta)

        ingresos_area = qs_ingresos.filter(
            area__isnull=False
        ).values(
            'area__nombre'
        ).annotate(
            total=Count('id')
        ).order_by('-total')

        ingresos_hora = qs_ingresos.annotate(
            hora=ExtractHour('fecha_creacion')
        ).values(
            'hora'
        ).annotate(
            total=Count('id')
        ).order_by('hora')

        context['areas_labels'] = json.dumps([x['area__nombre'] for x in ingresos_area])
        context['areas_data'] = json.dumps([x['total'] for x in ingresos_area])

        context['horas_labels'] = json.dumps([
            f"{int(x['hora']):02d}:00" for x in ingresos_hora if x['hora'] is not None
        ])
        context['horas_data'] = json.dumps([
            x['total'] for x in ingresos_hora if x['hora'] is not None
        ])

        context['kpi_total_ingresos'] = qs_ingresos.count()
        context['kpi_total_personas'] = qs_ingresos.exclude(
            persona__isnull=True
        ).values('persona_id').distinct().count()

        context['kpi_total_areas'] = qs_ingresos.exclude(
            area__isnull=True
        ).values('area_id').distinct().count()

        context['areas'] = Area.objects.filter(status=True).order_by('nombre')

        context['area_id'] = area_id
        context['fecha_desde'] = fecha_desde
        context['fecha_hasta'] = fecha_hasta

        return context
