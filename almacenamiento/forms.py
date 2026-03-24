from django import forms
from .models import Estante

class EstanteForm(forms.ModelForm):
    class Meta:
        model = Estante
        fields = '__all__'
        widgets = {
            'almacen': forms.Select(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django.shortcuts import render, redirect
from .forms import EstanteForm

def crear_estante(request):
    if request.method == 'POST':
        form = EstanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('estantes')
    else:
        form = EstanteForm()

    return render(request, 'crear_estante.html', {
        'form': form,
        'titulo': 'Registrar Estante'
    })