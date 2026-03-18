from django import forms
from .models import Devolucion

class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['numero_orden', 'producto', 'cantidad', 'motivo']
        labels = {
            'numero_orden': 'Número de orden',
            'producto': 'Producto',
            'cantidad': 'Cantidad',
            'motivo': 'Motivo de devolución',
        }
        widgets = {
            'numero_orden': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ORD-12345'
            }),
            'producto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el motivo...'
            }),
        }

    # ✅ MINE-101: Validaciones
    def clean_numero_orden(self):
        numero = self.cleaned_data.get('numero_orden')
        if not numero.strip():
            raise forms.ValidationError("El número de orden no puede estar vacío.")
        return numero.strip().upper()

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        if cantidad > 1000:
            raise forms.ValidationError("La cantidad no puede superar 1000 unidades.")
        return cantidad

    def clean_motivo(self):
        motivo = self.cleaned_data.get('motivo')
        if len(motivo.strip()) < 10:
            raise forms.ValidationError("El motivo debe tener al menos 10 caracteres.")
        return motivo.strip()