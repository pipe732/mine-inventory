from django import forms
from .models import Producto, Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de la categoría"}
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción (opcional)"}
            ),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["codigo_sku", "nombre", "descripcion", "stock", "categoria"]
        widgets = {
            "codigo_sku": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej: SKU-001"}
            ),
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del producto"}
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción (opcional)"}
            ),
            "stock": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
        }
        labels = {
            "codigo_sku": "Código / SKU",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "stock": "Stock / Cantidad",
            "categoria": "Categoría",
        }


class FiltroInventarioForm(forms.Form):
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Buscar por nombre o SKU...",
            }
        ),
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={"class": "form-select"}),
    )