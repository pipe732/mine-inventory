from django import forms
from .models import Estante, Almacen

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'detalles', 'capacidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del almacén'}),
            'detalles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles opcionales...'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }

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