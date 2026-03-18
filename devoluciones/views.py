# devoluciones/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DevolucionForm
from .models import Devolucion


def devoluciones_view(request):
    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Devolución registrada exitosamente.')
            return redirect('devoluciones')
    else:
        form = DevolucionForm()

    devoluciones = Devolucion.objects.all()

    return render(request, 'devoluciones.html', {  # ← sin subcarpeta
        'form':         form,
        'devoluciones': devoluciones,
    })