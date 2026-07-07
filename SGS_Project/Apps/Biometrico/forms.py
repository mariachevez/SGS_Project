from django import forms
from .models import Configuracion, Area


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['area', 'descripcion', 'activo']
        widgets = {
            'area': forms.Select(attrs={
                'class': 'form-select form-select-sm select2',
                'style': 'width: 100%;'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 3,
                'placeholder': 'Ingrese una descripción...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos para que solo muestre áreas activas si tu modelo Area posee status
        if 'area' in self.fields and hasattr(Area, 'status'):
            self.fields['area'].queryset = Area.objects.filter(status=True)

        self.fields['area'].empty_label = "Seleccione un área..."