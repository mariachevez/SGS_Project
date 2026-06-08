from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from ...models import *
from ...forms import *
from core.models import EliminarBase
from core.views import AjaxExceptionMixin
from django.db import transaction
from core.funciones import validar_cedula

class ListadoPersona(ListView):
    model = Persona
    template_name = 'Persona/index.html'
    paginate_by = 10
    context_object_name = 'personas'

    def get_queryset(self):
        return Persona.objects.filter(status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_tabla'] = 'Listado del Personal'
        return context
    
class CrearPersona(AjaxExceptionMixin, CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'Persona/form.html'
    success_url = reverse_lazy('listado_persona')
    
    def form_valid(self, form):
        persona = form.save(commit=False)
        cedula = form.cleaned_data.get('identificacion')
        email = form.cleaned_data.get('email')
        apellido1 = form.cleaned_data.get('apellido1') or ''
        apellido2 = form.cleaned_data.get('apellido2') or ''
        first_name = form.cleaned_data.get('nombres')
        last_name = f'{apellido1} {apellido2}'.strip()
        anio_nacimiento = form.cleaned_data.get('nacimiento').year
        try:
            with transaction.atomic():
                
                validar_cedula(cedula)
                
                password = f'{cedula}'+'*'+f'{anio_nacimiento}'
                print(password)
                
                user = User.objects.create_user(username=cedula, 
                                         first_name=first_name, 
                                         last_name=last_name, 
                                         email=email, 
                                         password=password)
                persona.user = user
                persona.save()
        except Exception as ex:
            form.add_error(None, str(ex))
            return self.form_invalid(form)
        messages.success(self.request, 'Se ha guardado exitosamente')
        self.object = persona
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form)
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('crear_persona')
        return context

class EditarPersona(AjaxExceptionMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'Persona/form.html'
    success_url = reverse_lazy('listado_persona')
    
    def form_valid(self, form):
        messages.success(self.request, 'Edición exitosa del registro')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardar'] = reverse('editar_persona', kwargs={'pk': self.object.pk})
        return context

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
        