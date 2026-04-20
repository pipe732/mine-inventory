# prestamo/forms.py
from django import forms
from django.utils import timezone
from .models import Prestamo


class PrestamoForm(forms.ModelForm):
    """Formulario para crear/editar un préstamo."""

    class Meta:
        model  = Prestamo
        fields = ['usuario', 'nombre_usuario', 'observaciones', 'fecha_vencimiento']
        labels = {
            'usuario':          'Documento / ID del usuario',
            'nombre_usuario':   'Nombre del usuario',
            'observaciones':    'Observaciones',
            'fecha_vencimiento': 'Fecha de vencimiento',
        }
        widgets = {
            'usuario': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Documento o ID',
                'id':          'id_usuario',
            }),
            'nombre_usuario': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Nombre completo del responsable',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Notas adicionales (opcional)...',
            }),
            'fecha_vencimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type':  'date',
                }
            ),
        }

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario', '').strip()
        if not usuario:
            raise forms.ValidationError('El documento/ID del usuario no puede estar vacío.')
        return usuario

    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get('fecha_vencimiento')
        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError('La fecha de vencimiento no puede ser en el pasado.')
        return fecha