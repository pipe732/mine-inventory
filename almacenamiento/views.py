from django.shortcuts import render, redirect, get_object_or_404
from .forms import EstanteForm, AlmacenForm
from .models import Estante, Almacen


def vista_almacenes(request):
    almacenes = Almacen.objects.all()
    form = AlmacenForm()

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear':
            form = AlmacenForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('almacenes')

        elif accion == 'editar':
            pk = request.POST.get('almacen_id')
            almacen = get_object_or_404(Almacen, pk=pk)
            form_editar = AlmacenForm(request.POST, instance=almacen)
            if form_editar.is_valid():
                form_editar.save()
                return redirect('almacenes')

        elif accion == 'eliminar':
            pk = request.POST.get('almacen_id')
            get_object_or_404(Almacen, pk=pk).delete()
            return redirect('almacenes')

    return render(request, 'almacenes.html', {
        'almacenes': almacenes,
        'form': form,
        'show_modal': bool(form.errors)
    })


def vista_estantes(request):
    estantes = Estante.objects.all()
    form = EstanteForm()

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear':
            form = EstanteForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('estantes')

        elif accion == 'editar':
            pk = request.POST.get('estante_id')
            estante = get_object_or_404(Estante, pk=pk)
            form_editar = EstanteForm(request.POST, instance=estante)
            if form_editar.is_valid():
                form_editar.save()
                return redirect('estantes')

        elif accion == 'eliminar':
            pk = request.POST.get('estante_id')
            get_object_or_404(Estante, pk=pk).delete()
            return redirect('estantes')

    return render(request, 'estantes.html', {
        'estantes': estantes,
        'almacenes': Almacen.objects.all(),
        'form': form,
        'show_modal': bool(form.errors)
    })


def crear_estante(request):
    return redirect('estantes')