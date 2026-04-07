# devoluciones/forms.py
from django import forms
from .models import Devolucion


class DevolucionEditForm(forms.ModelForm):
    class Meta:
        model   = Devolucion
        fields  = ['estado']
        labels  = {'estado': 'Estado'}
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }