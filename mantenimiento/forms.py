from django import forms
from .models import EstadoCondicion

class EstadoCondicionForm(forms.ModelForm):
    class Meta:
        model = EstadoCondicion
        #Campos del formulario para Registrar un tipo de estado
        fields = [
            'estado_material', 
            'codigo_abreviado', 
            'descripcion', 
            'categoria_estado', 
            'estado_disponibilidad', 
            'color'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # Si el campo es un select (como categoría), usamos form-select
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            # Para los demás campos de texto, usamos form-control
            else:
                field.widget.attrs.update({'class': 'form-control'})
                