from django import forms
from core.forms import FormModeloBase
from .models import *
from core.models import CoreChoices

class NuevaSolicitudForm(FormModeloBase):
    area = forms.ModelChoiceField(label='Área:', queryset=Area.objects.filter(status=True),
                                  help_text='Área en el que se realizará la notificación', 
                                  widget=forms.Select(attrs={'class': 'form-select select2', 'col': 6}))
    descripcion = forms.CharField(label='Descripción de su solicitud:',
                                  widget=forms.Textarea(attrs={'placeholder': 'Ejm: Solicitud para petición de intervención técnica y poder proceder con el acceso', 'rows': 4}))
    tipo_solicitud = forms.ChoiceField(label='Tipo de Solicitud:', choices=CoreChoices.TipoSolicitud, widget=forms.Select(attrs={'class': 'form-select', 'col': 6}))
    class Meta:
        model = Solicitudes
        fields = ['area', 'tipo_solicitud','descripcion']