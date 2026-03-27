# prestamos/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PrestamoForm
from .models import Prestamo


def prestamos_view(request):
    """
    MINE-120: guardar préstamo (POST)
    Listado de préstamos
    """
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            form.save()   # MINE-120: guardar préstamo
            messages.success(request, 'Préstamo registrado exitosamente.')
            return redirect('prestamo')
    else:
        form = PrestamoForm()

    prestamos = Prestamo.objects.all()

    return render(request, 'prestamo.html', {
        'form':      form,
        'prestamos': prestamos,
    })