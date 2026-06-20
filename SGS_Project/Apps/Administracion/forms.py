from django import forms
from django.db import transaction

from core.forms import FormModeloBase
from core.funciones import validar_cedula
from .models import *
from core.models import *
from .models import Persona


class PersonaForm(FormModeloBase):
    nombres = forms.CharField(label='Nombres:', widget=forms.TextInput(attrs={'col': '5', 'placeholder': 'Ejm: Juan Carlos'}))
    apellido1 = forms.CharField(label='Primer Apellido:', widget=forms.TextInput(attrs={'col': '4', 'placeholder': 'Ejm: Perez'}))
    apellido2 = forms.CharField(label='Segundo apellido', required=False, widget=forms.TextInput(attrs={'col': '3', 'placeholder': 'Ejm: Armijos'}))
    identificacion = forms.CharField(label='Cédula:', help_text='Máximo de 10 dígitos', min_length=10, max_length=10, widget=forms.TextInput(attrs={'col': '4', 'placeholder': 'Ejm: 010XXXXXXX'}))
    telefono = forms.CharField(label='Teléfono celular:', help_text='Máximo de 10 dígitos', min_length=10, max_length=10, widget=forms.TextInput(attrs={'col': '5', 'placeholder': 'Ejm: 09XXXXXXXX'}))
    email = forms.EmailField(label='Correo electrónico:', widget=forms.TextInput(attrs={'col': '7', 'placeholder': 'Ejm: correo@ejemplo.com'}))
    nacimiento = forms.DateField(label='Fecha de Nacimiento:', widget=forms.DateInput(attrs={'col': '4', 'type': 'date'}))
    sexo = forms.ChoiceField(label='Sexo:', choices=CoreChoices.Sexo.choices, widget=forms.Select(attrs={'class':'form-select','col':'4'}))
    pais = forms.ModelChoiceField(label='País:', queryset=Pais.objects.filter(status=True), widget=forms.Select(attrs={'col': '4', 'class': 'select2'}))
    provincia = forms.ModelChoiceField(label='Provincia:', queryset=Provincia.objects.none(), widget=forms.Select(attrs={'col': '4', 'class': 'select2'}))
    canton = forms.ModelChoiceField(label='Cantón', queryset=Canton.objects.none(), widget=forms.Select(attrs={'col': '4', 'class': 'select2'}))
    
    class Meta:
        model = Persona
        fields = ['nombres', 'apellido1', 'apellido2', 'identificacion', 'nacimiento', 'sexo', 'email', 'telefono', 'pais', 'provincia', 'canton']
    
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
                validar_cedula(cedula)  # Tu validador
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

        return persona
            
class PaisForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre del País:', widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ejm: Ecuador'}))
    prefijo = forms.CharField(label='Prefijo del país:', required=False, widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ejm: 593'}))
    
    class Meta:
        model = Pais
        fields = ['nombre', 'prefijo']
        
    def __init__(self, *args, **kwargs):
        super(PaisForm, self).__init__(*args, **kwargs)

class ProvinciaForm(FormModeloBase):
    pais = forms.ModelChoiceField(label='País:', queryset=Pais.objects.filter(status=True),  widget=forms.Select(attrs={'col':'12', 'class':'form-select'}))
    nombre = forms.CharField(label='Nombre de la Provincia:', widget=forms.TextInput(attrs={'col': '12', 'placeholder': 'Ejm: Guayas'}))
    
    class Meta:
        model = Provincia
        fields = ['pais', 'nombre']
    
    def __init__(self, *args, **kwargs):
        super(ProvinciaForm, self).__init__(*args, **kwargs)

class CantonForm(FormModeloBase):
    provincia = forms.ModelChoiceField(label='Provincia:', queryset=Provincia.objects.filter(status=True), widget=forms.Select(attrs={'class': 'form-select'}))
    nombre = forms.CharField(label='Nombre del Cantón:', widget=forms.TextInput(attrs={'placeholder': 'Ejm: Milagro'}))
    
    class Meta:
        model = Canton
        fields = ['provincia', 'nombre']
        
    def __init__(self, *args, **kwargs):
        super(CantonForm, self).__init__(*args, **kwargs)
    

class AreaForm(FormModeloBase):
    nombre = forms.CharField(label='Nombre del área:', widget=forms.TextInput(attrs={'placeholder': 'Ejm: Producción'}))
    descripcion = forms.CharField(label='Descripción del área:', widget=forms.Textarea(attrs={'placeholder': 'Ingrese una breve descripción del área', 'rows': '5'}))

    class Meta:
        model = Area
        fields = ['nombre', 'descripcion']
        
    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
        
class AsignacionDirectorForm(FormModeloBase):
    director = forms.ModelChoiceField(label='Responsable del Área:', queryset=Persona.objects.filter(status=True), widget=forms.Select(attrs={'class': 'form-select select2'}))
    
    class Meta:
        model = Area
        fields = ['director']
    
    def __init__(self, *args, **kwargs):
        super(AsignacionDirectorForm, self).__init__(*args, **kwargs)