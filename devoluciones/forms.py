# devoluciones/forms.py
from django import forms
from .models import Devolucion


class DevolucionEditForm(forms.ModelForm):
    class Meta:
        model   = Devolucion
        fields  = []
        labels  = {}
        widgets = {}