# prestamos/forms.py
from django import forms
from .models import Prestamo
from inventario.models import Producto


class PrestamoForm(forms.ModelForm):
    """MINE-118 / MINE-119 — Formulario con validaciones."""

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'),
        empty_label='— Selecciona una herramienta —',
        widget=forms.Select(attrs={'class': 'form-control form-select'}),
        label='Herramienta / Producto',
        to_field_name='nombre',
    )

    class Meta:
        model  = Prestamo
        fields = ['usuario', 'producto', 'cantidad', 'observaciones']
        labels = {
            'usuario':       'Usuario',
            'producto':      'Herramienta / Producto',
            'cantidad':      'Cantidad',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'usuario': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del usuario',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1,
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Notas adicionales (opcional)...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all().order_by('nombre')

    # MINE-119: validaciones
    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario', '').strip()
        if not usuario:
            raise forms.ValidationError('El nombre de usuario no puede estar vacío.')
        return usuario

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        if not producto:
            raise forms.ValidationError('Debes seleccionar una herramienta.')
        # Store product name string in the model field
        return producto.nombre

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        if cantidad > 500:
            raise forms.ValidationError('La cantidad no puede superar 500 unidades.')
        return cantidad