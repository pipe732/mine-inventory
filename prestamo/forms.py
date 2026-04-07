# prestamo/forms.py
from django import forms
from .models import Prestamo, ItemPrestamo
from inventario.models import Producto


class PrestamoForm(forms.ModelForm):
    """Formulario para crear un préstamo con un ítem inicial."""

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'),
        empty_label='— Selecciona una herramienta —',
        widget=forms.Select(attrs={'class': 'form-control form-select'}),
        label='Herramienta / Producto',
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        label='Cantidad',
    )

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

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        if cantidad > 500:
            raise forms.ValidationError('La cantidad no puede superar 500 unidades.')
        return cantidad

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        if not producto:
            raise forms.ValidationError('Debes seleccionar una herramienta.')
        if producto.stock == 0:
            raise forms.ValidationError(
                f'"{producto.nombre}" no tiene stock disponible.'
            )
        return producto

    def clean(self):
        cleaned = super().clean()
        producto = cleaned.get('producto')
        cantidad = cleaned.get('cantidad')
        # Validar que la cantidad no supere el stock disponible
        if producto and cantidad and cantidad > producto.stock:
            raise forms.ValidationError(
                f'Stock insuficiente: solo hay {producto.stock} unidad(es) '
                f'de "{producto.nombre}" disponibles.'
            )
        return cleaned

    def save(self, commit=True):
        """Guarda el Prestamo, crea el ItemPrestamo y descuenta el stock."""
        prestamo = super().save(commit=commit)
        if commit:
            producto = self.cleaned_data['producto']
            cantidad = self.cleaned_data['cantidad']
            ItemPrestamo.objects.create(
                prestamo=prestamo,
                producto=producto,
                cantidad=cantidad,
            )
            # Descontar stock al momento de crear el préstamo
            producto.stock -= cantidad
            producto.save(update_fields=['stock'])
        return prestamo