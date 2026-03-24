from django.shortcuts import render, redirect
from .forms import EstanteForm
from .models import Estante


def vista_estantes(request):
    estantes = Estante.objects.all()
    return render(request, 'almacenamiento/estantes.html', {
        'estantes': estantes
    })


def crear_estante(request):
    if request.method == 'POST':
        form = EstanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('estantes')
    else:
        form = EstanteForm()

    return render(request, 'almacenamiento/crear_estante.html', {
        'form': form
    })

