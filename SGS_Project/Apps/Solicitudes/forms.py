from django import forms
from core.forms import FormModeloBase
from .models import *
from core.models import CoreChoices


class NuevaSolicitudForm(FormModeloBase):
    area = forms.ModelChoiceField(label='Área:', queryset=Area.objects.filter(status=True),
                                  help_text='Área en el que se realizará la notificación',
                                  widget=forms.Select(attrs={'class': 'form-select select2', 'col': 6}))
    descripcion = forms.CharField(label='Descripción de su solicitud:',
                                  widget=forms.Textarea(attrs={
                                      'placeholder': 'Ejm: Solicitud para petición de intervención técnica y poder proceder con el acceso',
                                      'rows': 4}))
    tipo_solicitud = forms.ChoiceField(label='Tipo de Solicitud:', choices=CoreChoices.TipoSolicitud,
                                       widget=forms.Select(attrs={'class': 'form-select', 'col': 6}))
    archivo = forms.FileField(label='Archivo:', help_text='Cargue un archivo de tipo: PDF, JPG, JPEG o PNG', required=False,
                              widget=forms.FileInput())

    class Meta:
        model = Solicitudes
        fields = ['area', 'tipo_solicitud', 'descripcion', 'archivo']

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')

        if not archivo:
            return archivo

        extensiones_permitidas = ['.pdf', '.jpg', '.jpeg', '.png']
        tipos_permitidos = [
            'application/pdf',
            'image/jpeg',
            'image/png'
        ]

        extension = archivo.name.lower()

        if not any(extension.endswith(ext) for ext in extensiones_permitidas):
            raise forms.ValidationError(
                'Solo se permiten archivos PDF, JPG, JPEG o PNG.'
            )

        if archivo.content_type not in tipos_permitidos:
            raise forms.ValidationError(
                'El tipo de archivo no es válido.'
            )

        return archivo


class ResponderSolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitudes
        fields = ['estado_solicitud', 'respuesta_solicitud']
        widgets = {
            'estado_solicitud': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'respuesta_solicitud': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escriba aquí los fundamentos de la aprobación o rechazo...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_estado_solicitud(self):
        estado = self.cleaned_data.get('estado_solicitud')
        if estado == 'P':
            raise forms.ValidationError('Debe aprobar o rechazar la solicitud, no puede dejarla en pendiente.')
        return estado