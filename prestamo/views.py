# prestamos/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PrestamoForm
from .models import Prestamo
from inventario.models import Producto


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
    productos = Producto.objects.all().order_by('nombre')

    total_prestamos     = prestamos.count()
    prestamos_activos   = prestamos.filter(estado='activo').count()
    prestamos_devueltos = prestamos.filter(estado='devuelto').count()
    prestamos_vencidos  = prestamos.filter(estado='vencido').count()

    return render(request, 'prestamo.html', {
        'form':                form,
        'prestamos':           prestamos,
        'productos':           productos,
        'total_prestamos':     total_prestamos,
        'prestamos_activos':   prestamos_activos,
        'prestamos_devueltos': prestamos_devueltos,
        'prestamos_vencidos':  prestamos_vencidos,
    })