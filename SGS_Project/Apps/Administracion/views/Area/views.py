import json
from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView

from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView
from ...models import *
from ...forms import *
from core.models import EliminarBase
from core.views import AjaxExceptionMixin

class ListarArea(ListView):
    model = Area
    template_name = 'Area/index.html'
    paginate_by = 10
    context_object_name = 'areas'
    
    def get_queryset(self):
        return Area.objects.filter(status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado de Áreas'
        return context
    
class CrearArea(BaseCreateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AreaForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_area')
        return context
    
class EditarArea(BaseUpdateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AreaForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_area', kwargs={'pk': self.object.pk})
        return context
    
class EliminarArea(BaseDeleteView):
    model = Area
    redirect_url = reverse_lazy('listado_areas')
    
class AsignarDirectorArea(BaseUpdateView):
    model = Area
    template_name = 'formulario.html'
    form_class = AsignacionDirectorForm
    success_url = reverse_lazy('listado_areas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('asignar_director', kwargs={'pk': self.object.pk})
        return context

class AgregarResponsables(AjaxExceptionMixin, View):
    template_name = 'Area/personalformulario.html'
    def get(self, request, pk): 
        area = Area.objects.get(status=True, pk=pk)
        personas = Persona.objects.filter(status=True, areas_trabajo__isnull=True, areas_dirigidas__isnull=True)
        if not area:
            return JsonResponse({'result': False, 'mensaje': 'Error al obtener el área'})
    
        return render(request, self.template_name, {'area': area, 'personas': personas})
    
    def post(self, request, pk):
        area = Area.objects.filter(status=True, pk=pk)
        if not area:
            return JsonResponse({'result': False, 'mensaje': 'No es área válido'})
        
        try:
            personas = json.loads(request.POST['personas_list'])
        except Exception as ex:
            return JsonResponse({'result': False, 'mensaje': f'{ex}'})

class BuscarPersona(View):
    
    def get(self, request):
        persona = request.GET.get('id')
        if not persona:
            return JsonResponse({'result': False, 'mensaje': 'Por favor, seleccione una persona'})
        persona = Persona.objects.get(pk=persona)
        return JsonResponse({'result': True,
                             'id': persona.pk,
                             'foto': request.build_absolute_uri(persona.get_foto()), 
                             'nombres': persona.nombre_completo_minus(), 
                             'identificacion': persona.identificacion})

class GuardarAsignacion(AjaxExceptionMixin, View):
    def post(self, request):
        try:
            ePersona = request.POST.get('persona_id')
            area = request.POST.get('area_id')
            personas_list = []
            if not ePersona:
                return JsonResponse({'result': False, 'mensaje': 'Seleccione una persona'})
            if not area:
                return JsonResponse({'result': False, 'mensaje': 'No se recibió un área'})
            
            persona_existe = AreaPersona.objects.filter(area_id=area, persona_id=ePersona, status=True)
            if not persona_existe.exists():
                AreaPersona(area_id=area, persona_id=ePersona).save(request)
                personas = Persona.objects.filter(status=True, areas_trabajo__isnull=True, areas_dirigidas__isnull=True)
                for persona in personas:
                    personas_list.append({'id': persona.pk, 'nombres': persona.nombre_completo_minus()})
                return JsonResponse({'result': True, 'personas': personas_list})
            else:
                return JsonResponse({'result': False, 'mensaje': 'Esta persona ya está actualmente en un área'})
        except Exception as ex:
            return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})
        