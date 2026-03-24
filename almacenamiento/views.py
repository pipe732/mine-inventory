from django.shortcuts import render, redirect
from .forms import EstanteForm
from .models import Estante


def vista_estantes(request):
    estantes = Estante.objects.all()
    form = EstanteForm()

    if request.method == 'POST':
        form = EstanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('estantes')

    return render(request, 'almacenamiento/estantes.html', {
        'estantes': estantes,
        'form': form,
        'show_modal': form.errors  # reabre el modal si hubo errores
    })


def crear_estante(request):
    return redirect('estantes')