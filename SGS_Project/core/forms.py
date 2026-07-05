from django import forms
from django.utils.safestring import mark_safe


class FormModeloBase(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # kwargs['excluir'] += ['status', 'usuario_creacion', 'fecha_creacion', 'usuario_modificacion', 'fecha_modificacion', 'usuario']
        no_requeridos = kwargs.pop('no_requeridos', [])
        requeridos = kwargs.pop('requeridos', [])
        # excluir = kwargs.pop('excluir', [])

        super().__init__(*args, **kwargs)

        # for campo in excluir:
            # if campo in self.fields:
                # self.fields.pop(campo)

        for nr in no_requeridos:
            if nr in self.fields:
                self.fields[nr].required = False

        for r in requeridos:
            if r in self.fields:
                self.fields[r].required = True

        for name, field in self.fields.items():
            col = field.widget.attrs.pop('col', '12')
            field.col = col

            if isinstance(field, forms.DateField) or isinstance(field.widget, forms.DateInput):
                field.widget.format = '%Y-%m-%d'
                field.widget.attrs['type'] = 'date'

            if isinstance(field.widget, forms.Select):
                clase = 'form-select'
            else:
                clase = 'form-control'
            
            if isinstance(field, forms.ChoiceField) and not isinstance(field, forms.ModelChoiceField):
                choices = list(field.choices)

                if choices and choices[0][0] != '':
                    field.choices = [('', 'Seleccione una opción')] + choices

            # Para ModelChoiceField
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = 'Seleccione una opción'

            clases_actuales = field.widget.attrs.get('class', '')

            if clase not in clases_actuales:
                field.widget.attrs['class'] = f'{clases_actuales} {clase}'.strip()

            # Label obligatorio
            if field.required and field.label:
                field.label = mark_safe(
                    f'{field.label}<span class="text-danger ms-1"><strong>*</strong></span>'
                )
    def clean(self):
        cleaned_data = super().clean()

        for nombre, field in self.fields.items():

            if (
                isinstance(field, forms.CharField)
                and isinstance(field.widget, forms.TextInput)
                and not isinstance(field, forms.EmailField)
            ):
                valor = cleaned_data.get(nombre)

                if isinstance(valor, str):
                    cleaned_data[nombre] = valor.upper()

        return cleaned_data