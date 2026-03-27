from django import forms
from .models import Estante

class EstanteForm(forms.ModelForm):
    class Meta:
        model = Estante
        fields = ['almacen', 'codigo', 'detalles', 'capacidad']
        widgets = {
            'almacen': forms.Select(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'detalles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }