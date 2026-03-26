from django.shortcuts import render, redirect
from .forms import EstanteForm, AlmacenForm
from .models import Estante, Almacen


def vista_almacenes(request):
    almacenes = Almacen.objects.all()
    form = AlmacenForm()

    if request.method == 'POST':
        form = AlmacenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('almacenes')

    return render(request, 'almacenes.html', {
        'almacenes': almacenes,
        'form': form,
        'show_modal': bool(form.errors)
    })


def vista_estantes(request):
    if request.method == 'POST':
        form = EstanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('estantes')
    else:
        form = EstanteForm()

    estantes = Estante.objects.all()

    return render(request, 'estantes.html', {
        'estantes': estantes,
        'form': form,
        'show_modal': bool(form.errors)
    })


def crear_estante(request):
    return redirect('estantes')