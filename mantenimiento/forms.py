from django import forms
from .models import TipoEstado

class TipoEstadoForm(forms.ModelForm):
    class Meta:
        model = TipoEstado
        fields = ['nombre', 'codigo', 'descripcion', 'categoria', 
                'impacto_disponibilidad', 'color', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Dañado severo'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: DS'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'impacto_disponibilidad': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-25'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del estado *',
            'codigo': 'Código abreviado *',
            'descripcion': 'Descripción breve',
            'categoria': 'Categoría',
            'impacto_disponibilidad': 'Impacto en disponibilidad *',
            'color': 'Color asociado (opcional)',
            'activo': 'Estado activo',
        }