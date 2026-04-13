# prestamo/forms.py
from django import forms
from .models import Prestamo


class PrestamoForm(forms.ModelForm):
    """Formulario para crear un préstamo. Los ítems (producto/cantidad)
    se procesan directamente en la vista como listas múltiples."""

    class Meta:
        model  = Prestamo
        fields = ['usuario', 'observaciones']
        labels = {
            'usuario':       'Usuario',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'usuario': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del usuario',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Notas adicionales (opcional)...',
            }),
        }

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario', '').strip()
        if not usuario:
            raise forms.ValidationError('El nombre de usuario no puede estar vacío.')
        return usuario