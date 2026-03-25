# devoluciones/forms.py
from django import forms
from .models import Devolucion


class DevolucionForm(forms.ModelForm):
    """Formulario para crear una devolución (sin campo estado)."""

    class Meta:
        model  = Devolucion
        fields = ['numero_orden', 'producto', 'cantidad', 'motivo']
        labels = {
            'numero_orden': 'Número de orden',
            'producto':     'Producto',
            'cantidad':     'Cantidad',
            'motivo':       'Motivo de devolución',
        }
        widgets = {
            'numero_orden': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: ORD-12345',
            }),
            'producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del producto',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1,
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Describe el motivo...',
            }),
        }

    def clean_numero_orden(self):
        numero = self.cleaned_data.get('numero_orden', '').strip()
        if not numero:
            raise forms.ValidationError('El número de orden no puede estar vacío.')
        return numero.upper()

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        if cantidad > 1000:
            raise forms.ValidationError('La cantidad no puede superar 1000 unidades.')
        return cantidad

    def clean_motivo(self):
        motivo = self.cleaned_data.get('motivo', '').strip()
        if len(motivo) < 10:
            raise forms.ValidationError('El motivo debe tener al menos 10 caracteres.')
        return motivo


class DevolucionEditForm(forms.ModelForm):
    """
    MINE-106 / MINE-108 / MINE-109
    Formulario de edición: incluye todos los campos + estado.
    """

    class Meta:
        model  = Devolucion
        fields = ['numero_orden', 'producto', 'cantidad', 'motivo', 'estado']
        labels = {
            'numero_orden': 'Número de orden',
            'producto':     'Producto',
            'cantidad':     'Cantidad',
            'motivo':       'Motivo de devolución',
            'estado':       'Estado',
        }
        widgets = {
            'numero_orden': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: ORD-12345',
            }),
            'producto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del producto',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1,
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
            }),
            # MINE-108: campo de estado como select
            'estado': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def clean_numero_orden(self):
        numero = self.cleaned_data.get('numero_orden', '').strip()
        if not numero:
            raise forms.ValidationError('El número de orden no puede estar vacío.')
        return numero.upper()

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        if cantidad > 1000:
            raise forms.ValidationError('La cantidad no puede superar 1000 unidades.')
        return cantidad

    def clean_motivo(self):
        motivo = self.cleaned_data.get('motivo', '').strip()
        if len(motivo) < 10:
            raise forms.ValidationError('El motivo debe tener al menos 10 caracteres.')
        return motivo