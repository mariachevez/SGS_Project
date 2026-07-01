from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView
from SGS_Project.forms_utils import BaseCreateView, BaseUpdateView, BaseDeleteView
from ...models import *
from ...forms import *
from core.models import EliminarBase
from core.views import AjaxExceptionMixin
from django.db import transaction
from core.funciones import validar_cedula

class ListadoPersona(ListView):
    model = Persona
    template_name = 'Persona/index.html'
    paginate_by = 25
    context_object_name = 'personas'

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('s')
        estado = self.request.GET.get('estado')

        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) |
                Q(apellido1__icontains=search) |
                Q(apellido2__icontains=search) |
                Q(identificacion__icontains=search) |
                Q(usuario__username__icontains=search)
            )

        if estado in ['true', 'false']:
            val_bool = estado == 'true'
            queryset = queryset.filter(status=val_bool)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado del Personal'
        context['url_formcrear'] = reverse('crear_persona')
        context['titulo'] = 'Registrar Personal'
        context['s'] = self.request.GET.get('s')
        context['estado'] = self.request.GET.get('estado')
        return context

class CrearPersona(BaseCreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'Persona/form.html'
    success_url = reverse_lazy('listado_persona')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_persona')
        return context

    def form_valid(self, form):
        try:
            # Al llamar al super, la clase base llamará a form.save(),
            # ejecutando la lógica interna del formulario, guardando la FK,
            # haciendo los logs de auditoría y respondiendo el JSON correcto.
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)

class EditarPersona(BaseUpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'Persona/form.html'
    success_url = reverse_lazy('listado_persona')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_persona', kwargs={'pk': self.object.pk})
        return context

    def form_valid(self, form):
        try:
            # Al llamar al super, la clase base llamará a form.save(),
            # ejecutando la lógica interna del formulario, guardando la FK,
            # haciendo los logs de auditoría y respondiendo el JSON correcto.
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)

class InactivarPersona(BaseDeleteView):
    model = Persona
    redirect_url = reverse_lazy('listado_persona')

class ObtenerProvincias(View):
    def get(self, request):
        try:
            pais_id = request.GET.get('id')
            pronvicia_list = []
            if pais_id:
                provincias = Provincia.objects.filter(pais_id=pais_id, status=True)
                if provincias:
                    for provincia in provincias:
                        pronvicia_list.append({'id': provincia.id, 'nombre': provincia.nombre})
                    return JsonResponse({'result': True, 'provincias': pronvicia_list})
                else:
                    return JsonResponse({'result': False, 'mensaje': f'No hay registros de provincias para este país'})
        except Exception as ex:
            return JsonResponse({'result': False, 'mensaje': f'{ex}'})

class ObtenerCantones(View):
    def get(self, request):
        try:
            provincia_id = request.GET.get('id')
            cantones_list = []
            if provincia_id:
                cantones = Canton.objects.filter(provincia_id=provincia_id, status=True)
                if cantones:
                    for canton in cantones:
                        cantones_list.append({'id': canton.id, 'nombre': canton.nombre})
                    return JsonResponse({'result': True, 'cantones': cantones_list})
                else:
                    return JsonResponse({'result': False, 'mensaje': 'No se encontraron cantones relacionados'})
        except Exception as ex:
            return JsonResponse({'result': False, 'mensaje': f'{ex}'})

class ListadoGrupoPersona(ListView):
    model = GrupoPersona
    template_name = 'GrupoPersona/index.html'
    paginate_by = 25
    context_object_name = 'grupo_personas'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('grupo', 'persona')
        persona_id = self.kwargs['persona_id']
        if persona_id:
            queryset = queryset.filter(persona_id=persona_id, status=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        persona_id = self.kwargs['persona_id']
        ePersona = Persona.objects.get(pk=persona_id)
        context['nombre_tabla'] = f'Grupos en los que se encuentra enrolado: {ePersona.nombre_completo_minus()}'
        context['url_formcrear'] = reverse('enrolar_persona', kwargs={'persona_id': self.kwargs['persona_id']})
        context['titulo'] = 'Enrolar persona a grupo'
        context['ret'] = reverse_lazy('listado_persona')
        context['s'] = self.request.GET.get('s')
        return context

class CrearGrupoPersona(BaseCreateView):
    model = GrupoPersona
    form_class = PersonaGruposForm
    template_name = 'formulario.html'

    def get_persona(self):
        return get_object_or_404(Persona, pk=self.kwargs['persona_id'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['persona'] = self.get_persona()
        return kwargs

    def get_success_url(self):
        return reverse('listado_grupos_persona', kwargs={'persona_id': self.kwargs['persona_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = self.get_persona()
        context['guardar'] = reverse('enrolar_persona', kwargs={'persona_id': self.kwargs['persona_id']})
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)


class InactivarGrupoPersona(BaseDeleteView):
    model = GrupoPersona
    redirect_url = reverse_lazy('listado_grupo_persona')
        