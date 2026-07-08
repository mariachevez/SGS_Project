from django import forms
from django.db import transaction
from django.urls import reverse_lazy

from core.forms import FormModeloBase
from core.funciones import validar_cedula
from .models import *
from core.models import *
from .models import Persona


class PersonaForm(FormModeloBase):
    nombres = forms.CharField(label='Nombres:',
                              widget=forms.TextInput(attrs={'col': '5', 'placeholder': 'Ejm: Juan Carlos'}))
    apellido1 = forms.CharField(label='Primer Apellido:',
                                widget=forms.TextInput(attrs={'col': '4', 'placeholder': 'Ejm: Perez'}))
    apellido2 = forms.CharField(label='Segundo apellido', required=False,
                                widget=forms.TextInput(attrs={'col': '3', 'placeholder': 'Ejm: Armijos'}))
    identificacion = forms.CharField(label='Cédula:', help_text='Máximo de 10 dígitos', min_length=10, max_length=10,
                                     widget=forms.TextInput(attrs={'col': '4', 'placeholder': 'Ejm: 010XXXXXXX'}))
    telefono = forms.CharField(label='Teléfono celular:', help_text='Máximo de 10 dígitos', min_length=10,
                               max_length=10,
                               widget=forms.TextInput(attrs={'col': '5', 'placeholder': 'Ejm: 09XXXXXXXX'}))
    email = forms.EmailField(label='Correo electrónico:',
                             widget=forms.TextInput(attrs={'col': '7', 'placeholder': 'Ejm: correo@ejemplo.com'}))
    nacimiento = forms.DateField(label='Fecha de Nacimiento:',
                                 widget=forms.DateInput(attrs={'col': '4', 'type': 'date'}))
    sexo = forms.ChoiceField(label='Sexo:', choices=CoreChoices.Sexo.choices,
                             widget=forms.Select(attrs={'class': 'form-select', 'col': '4'}))
    pais = forms.ModelChoiceField(label='País:', queryset=Pais.objects.filter(status=True),
                                  widget=forms.Select(attrs={'col': '4', 'class': 'select2'}))
    provincia = forms.ModelChoiceField(label='Provincia:', queryset=Provincia.objects.none(),
                                       widget=forms.Select(attrs={'col': '4', 'class': 'select2'}))
    canton = forms.ModelChoiceField(label='Cantón', queryset=Canton.objects.none(),
                                    widget=forms.Select(attrs={'col': '4', 'class': 'select2'}))

    class Meta:
        model = Persona
        fields = ['nombres', 'apellido1', 'apellido2', 'identificacion', 'nacimiento', 'sexo', 'email', 'telefono',
                  'pais', 'provincia', 'canton']

    def __init__(self, *args, **kwargs):
        super(PersonaForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['identificacion'].disabled = True
            self.fields['provincia'].queryset = Provincia.objects.filter(status=True,
                                                                         pais=self.instance.pais)
            self.fields['canton'].queryset = Canton.objects.filter(status=True,
                                                                   provincia=self.instance.provincia)

        for field in self.fields:
            self.fields[field].error_messages = {'required': 'Este campo es obligatorio'}

        if 'pais' in self.data:
            try:
                pais_id = int(self.data.get('pais'))
                self.fields['provincia'].queryset = Provincia.objects.filter(status=True, pais_id=pais_id)
            except (ValueError, TypeError):
                pass
        if 'provincia' in self.data:
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['canton'].queryset = Canton.objects.filter(status=True, provincia_id=provincia_id)
            except (ValueError, TypeError):
                pass

    def save(self, commit=True):
        # 1. Obtenemos la instancia en memoria que Django preparó
        persona = super().save(commit=False)

        # 2. Si es un registro nuevo (no tiene ID aún), creamos su usuario
        if not persona.pk:
            cedula = self.cleaned_data.get('identificacion')
            email = self.cleaned_data.get('email')
            apellido1 = self.cleaned_data.get('apellido1') or ''
            apellido2 = self.cleaned_data.get('apellido2') or ''
            first_name = self.cleaned_data.get('nombres')
            last_name = f'{apellido1} {apellido2}'.strip()
            nacimiento = self.cleaned_data.get('nacimiento')
            anio_nacimiento = nacimiento.year if nacimiento else "2000"

            # Ejecutamos todo seguro en una transacción
            with transaction.atomic():
                # validar_cedula(cedula)  # Tu validador
                existe_cedula = Persona.objects.filter(identificacion=cedula).exists()
                if existe_cedula:
                    raise ValueError(f'La cedula ingresada ya se encuentra registrada.')

                password = f'{cedula}*{anio_nacimiento}'
                user = User.objects.create_user(
                    username=cedula,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password
                )
                # Vinculamos el usuario a la persona
                persona.usuario = user
                try:
                    persona.save()
                except Exception as ex:
                    print(f"Error al guardar la persona: {ex}")
                    raise ValueError("Error al guardar la persona")
                    # CASO 2: Es una EDICIÓN (ya tiene ID)
        else:
            if persona.usuario:
                user = persona.usuario
                apellido1 = self.cleaned_data.get('apellido1') or ''
                apellido2 = self.cleaned_data.get('apellido2') or ''

                user.first_name = self.cleaned_data.get('nombres')
                user.last_name = f'{apellido1} {apellido2}'.strip()
                user.email = self.cleaned_data.get('email')
                user.save()

                if commit:
                    persona.save()

        return persona


class PaisForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre del País:',
                             widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ejm: Ecuador'}))
    prefijo = forms.CharField(label='Prefijo del país:', required=False,
                              widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ejm: 593'}))

    class Meta:
        model = Pais
        fields = ['nombre', 'prefijo']

    def __init__(self, *args, **kwargs):
        super(PaisForm, self).__init__(*args, **kwargs)


class ProvinciaForm(FormModeloBase):
    pais = forms.ModelChoiceField(label='País:', queryset=Pais.objects.filter(status=True),
                                  widget=forms.Select(attrs={'col': '12', 'class': 'form-select'}))
    nombre = forms.CharField(label='Nombre de la Provincia:',
                             widget=forms.TextInput(attrs={'col': '12', 'placeholder': 'Ejm: Guayas'}))

    class Meta:
        model = Provincia
        fields = ['pais', 'nombre']

    def __init__(self, *args, **kwargs):
        super(ProvinciaForm, self).__init__(*args, **kwargs)


class CantonForm(FormModeloBase):
    provincia = forms.ModelChoiceField(label='Provincia:', queryset=Provincia.objects.filter(status=True),
                                       widget=forms.Select(attrs={'class': 'form-select'}))
    nombre = forms.CharField(label='Nombre del Cantón:', widget=forms.TextInput(attrs={'placeholder': 'Ejm: Milagro'}))

    class Meta:
        model = Canton
        fields = ['provincia', 'nombre']

    def __init__(self, *args, **kwargs):
        super(CantonForm, self).__init__(*args, **kwargs)


class AreaForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre del área:', widget=forms.TextInput(attrs={'placeholder': 'Ejm: Producción'}))
    director = forms.ModelChoiceField(label='Director departamental', queryset=Persona.objects.filter(status=True),
                                      widget=forms.Select(attrs={'class': 'form-select', 'data-tipo': 'director', 'data-api': 'true',
                                                                 'data-url': reverse_lazy('buscar_personas')}))
    descripcion = forms.CharField(label='Descripción del área:', widget=forms.Textarea(
        attrs={'placeholder': 'Ingrese una breve descripción del área', 'rows': '5'}))

    class Meta:
        model = Area
        fields = ['nombre', 'director', 'descripcion']

    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)

        director_id = None
        if self.instance and self.instance.pk:
            director_id = self.instance.director_id
        elif self.is_bound:
            director_id = self.data.get(self.add_prefix('director'))

        if director_id:
            self.fields['director'].queryset = Persona.objects.filter(pk=director_id)


class AsignacionDirectorForm(FormModeloBase):
    director = forms.ModelChoiceField(label='Responsable del Área:', queryset=Persona.objects.filter(status=True),
                                      widget=forms.Select(attrs={'class': 'form-select select2'}))

    class Meta:
        model = Area
        fields = ['director']

    def __init__(self, *args, **kwargs):
        super(AsignacionDirectorForm, self).__init__(*args, **kwargs)


class GrupoForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre del Grupo:',
                             widget=forms.TextInput(attrs={'col': '12', 'placeholder': 'Ejm: Administrador'}))
    descripcion = forms.CharField(label='Descripción del grupo:', required=False,
                                  widget=forms.Textarea(
                                      attrs={'rows': '3', 'placeholder': 'Ejm: Descripcion del grupo'}))

    class Meta:
        model = Grupo
        fields = ['nombre', 'descripcion']

    def __init__(self, *args, **kwargs):
        super(GrupoForm, self).__init__(*args, **kwargs)


class CategoriaForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre de la Categoría:',
                             widget=forms.TextInput(attrs={'placeholder': 'Ejm: Administrativo'}))
    prioridad = forms.IntegerField(label='Prioridad', widget=forms.NumberInput())

    class Meta:
        model = ModuloCategorias
        fields = ['nombre', 'prioridad']

    def __init__(self, *args, **kwargs):
        super(CategoriaForm, self).__init__(*args, **kwargs)


class PersonaGruposForm(FormModeloBase):
    class Meta:
        model = GrupoPersona
        fields = ['grupo']
        widgets = {
            'grupo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.persona = kwargs.pop('persona', None)
        super().__init__(*args, **kwargs)
        if self.fields['grupo'].queryset is not None:
            self.fields['grupo'].queryset = Grupo.objects.filter(status=True).order_by('nombre')

    def clean_grupo(self):
        grupo = self.cleaned_data.get('grupo')
        if not grupo:
            raise forms.ValidationError('Seleccione un grupo')

        if grupo and self.persona:
            existe = GrupoPersona.objects.filter(
                persona=self.persona,
                grupo=grupo,
                status=True
            ).exists()
            if existe:
                raise forms.ValidationError('Esta persona ya se encuentra enrolada en este grupo.')
        return grupo

    def save(self, commit=True):
        grupopersona = super().save(commit=False)
        grupopersona.persona = self.persona
        if commit:
            grupopersona.save()
        return grupopersona


class ModuloCategoriasForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre de la Categoría:', required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Ejm: Administración'}))
    prioridad = forms.IntegerField(label='Prioridad de la Categoría:', required=True,
                                   widget=forms.NumberInput(attrs={'placeholder': 'Ejm: 1'}))

    class Meta:
        model = ModuloCategorias
        fields = ['nombre', 'prioridad']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'prioridad': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class GrupoModuloForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre del Grupo del módulo:',
                             widget=forms.TextInput(attrs={'placeholder': 'Describa el nombre del grupo de módulo'}))
    descripcion = forms.CharField(label='Descripción breve:', widget=forms.Textarea(
        attrs={'placeholder': 'Realice una descripción breve del grupo módulo', 'rows': 3}))

    class Meta:
        model = GrupoModulo
        fields = ['nombre', 'descripcion']


class ModuloForm(FormModeloBase):
    url = forms.CharField(label='URL del módulo:',
                          widget=forms.TextInput(attrs={'placeholder': 'Ejm: /administracion/listado'}))
    nombre = forms.CharField(label='Nombre del módulo:', widget=forms.TextInput(attrs={'placeholder': 'Ejm: Persona'}))
    icono = forms.CharField(label='Icono del módulo:',
                            widget=forms.TextInput(attrs={'placeholder': 'Ejm: fa-solid fa-users'}))
    descripcion = forms.CharField(label='Descripción del módulo:', widget=forms.Textarea(
        attrs={'placeholder': 'Ejm: Descripción breve del módulo', 'rows': 3}))
    activo = forms.BooleanField(label='Activo:', required=False,
                                widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'col': 3}))
    categorias = forms.ModelChoiceField(label='Categoría del Módulo', required=True,
                                        queryset=ModuloCategorias.objects.filter(status=True).order_by('prioridad',
                                                                                                       'nombre'),
                                        widget=forms.Select(attrs={'class': 'form-select'}))
    submodulo = forms.BooleanField(label='¿Es submódulo?', required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'col': 3}))

    class Meta:
        model = Modulo
        fields = ['categorias', 'icono', 'url', 'nombre', 'descripcion', 'activo', 'submodulo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AgruparModuloForm(FormModeloBase):
    class Meta:
        model = AgrupacionModulos
        fields = ['modulo', 'grupo_modulo']
        widgets = {
            'modulo': forms.Select(attrs={'class': 'form-select'}),
            'grupo_modulo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.grupo_modulo_id = kwargs.pop('grupo_modulo_id', None)
        self.modulo_id = kwargs.pop('modulo_id', None)
        super().__init__(*args, **kwargs)

        if self.grupo_modulo_id:
            # Caso 1: vienes desde el Grupo -> seleccionas el Módulo
            del self.fields['grupo_modulo']
            self.fields['modulo'].queryset = Modulo.objects.filter(status=True).order_by('nombre')

        elif self.modulo_id:
            # Caso 2: vienes desde el Módulo -> seleccionas el Grupo
            del self.fields['modulo']
            self.fields['grupo_modulo'].queryset = GrupoModulo.objects.filter(status=True).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        modulo = cleaned_data.get('modulo') if self.grupo_modulo_id else None
        grupo_modulo = cleaned_data.get('grupo_modulo') if self.modulo_id else None

        if self.grupo_modulo_id and modulo:
            existe = AgrupacionModulos.objects.filter(
                grupo_modulo_id=self.grupo_modulo_id,
                modulo=modulo,
                status=True
            ).exists()
            if existe:
                raise forms.ValidationError('Este módulo ya está agrupado en este grupo.')

        if self.modulo_id and grupo_modulo:
            existe = AgrupacionModulos.objects.filter(
                modulo_id=self.modulo_id,
                grupo_modulo=grupo_modulo,
                status=True
            ).exists()
            if existe:
                raise forms.ValidationError('Este grupo ya tiene asociado este módulo.')

        return cleaned_data

    def save(self, commit=True):
        agrupacion = super().save(commit=False)
        if self.grupo_modulo_id:
            agrupacion.grupo_modulo_id = self.grupo_modulo_id
        if self.modulo_id:
            agrupacion.modulo_id = self.modulo_id
        if commit:
            agrupacion.save()
        return agrupacion


class AgrupacionModulosPersonaForm(FormModeloBase):
    class Meta:
        model = AgrupacionModulosPersona
        fields = ['grupo_persona', 'grupo_modulo']
        widgets = {
            'grupo_persona': forms.Select(attrs={'class': 'form-select'}),
            'grupo_modulo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo_persona'].queryset = Grupo.objects.filter(status=True).order_by('nombre')
        self.fields['grupo_modulo'].queryset = GrupoModulo.objects.filter(status=True).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        grupo_persona = cleaned_data.get('grupo_persona')
        grupo_modulo = cleaned_data.get('grupo_modulo')

        if grupo_modulo and grupo_persona:
            queryset = AgrupacionModulosPersona.objects.filter(
                grupo_modulo=grupo_modulo,
                grupo_persona=grupo_persona,
                status=True
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('Esta combinación de grupo de módulos y grupo de personas ya existe.')

        return cleaned_data
