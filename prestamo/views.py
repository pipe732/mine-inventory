# prestamo/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .forms import PrestamoForm
from .models import Prestamo, ItemPrestamo
from inventario.models import Producto


def prestamos_view(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')

        # ── Cancelar préstamo (MINE-125 / MINE-126) ──
        if accion == 'cancelar':
            prestamo = get_object_or_404(Prestamo, pk=request.POST.get('prestamo_pk'))
            for item in prestamo.items.filter(devuelto=False):
                item.producto.stock += item.cantidad
                item.producto.save()
                item.devuelto = True
                item.save()
            prestamo.estado = 'devuelto'
            prestamo.save()
            messages.success(request, f'Préstamo #{prestamo.pk} cancelado y stock repuesto.')
            return redirect('prestamo')

        # ── Editar préstamo (MINE-141 / MINE-142) ──
        elif accion == 'editar':
            prestamo = get_object_or_404(Prestamo, pk=request.POST.get('prestamo_pk'))
            prestamo.estado = request.POST.get('estado', prestamo.estado)
            prestamo.observaciones = request.POST.get('observaciones', '')
            usuario_str = request.POST.get('usuario', '').strip()
            if usuario_str:
                prestamo.usuario = usuario_str
            prestamo.save()
            messages.success(request, f'Préstamo #{prestamo.pk} actualizado.')
            return redirect('prestamo')

        # ── Eliminar préstamo (MINE-127) ──
        elif accion == 'eliminar':
            prestamo = get_object_or_404(Prestamo, pk=request.POST.get('prestamo_pk'))
            for item in prestamo.items.filter(devuelto=False):
                item.producto.stock += item.cantidad
                item.producto.save()
            prestamo.delete()
            messages.success(request, 'Préstamo eliminado correctamente.')
            return redirect('prestamo')

        # ── Devolver ítem individual (MINE-137 / MINE-138) ──
        elif accion == 'devolver_item':
            item = get_object_or_404(ItemPrestamo, pk=request.POST.get('item_pk'))
            cantidad = int(request.POST.get('cantidad_devuelta', item.cantidad))
            cantidad = max(1, min(cantidad, item.cantidad))
            item.producto.stock += cantidad
            item.producto.save()
            item.devuelto = True
            item.save()
            # Si todos los ítems del préstamo están devueltos → marcar como devuelto
            prestamo = item.prestamo
            if not prestamo.items.filter(devuelto=False).exists():
                prestamo.estado = 'devuelto'
                prestamo.save()
            messages.success(request, f'Ítem "{item.producto.nombre}" devuelto correctamente.')
            return redirect('prestamo')

        # ── Crear nuevo préstamo (multi-ítem) ──
        else:
            form = PrestamoForm(request.POST)
            if form.is_valid():
                # Leer listas de productos y cantidades enviadas desde el modal
                producto_ids = request.POST.getlist('producto[]')
                cantidades   = request.POST.getlist('cantidad[]')

                # Filtrar filas vacías (select sin selección)
                items_raw = [
                    (pid, qty)
                    for pid, qty in zip(producto_ids, cantidades)
                    if pid
                ]

                # Validar que haya al menos un ítem
                if not items_raw:
                    form.add_error(None, 'Debes seleccionar al menos una herramienta.')
                else:
                    # Validar stock para cada ítem antes de guardar nada
                    errores = []
                    items_validated = []
                    for pid, qty_str in items_raw:
                        try:
                            producto = Producto.objects.get(pk=pid)
                        except Producto.DoesNotExist:
                            errores.append(f'Producto con id {pid} no existe.')
                            continue
                        try:
                            cantidad = int(qty_str)
                            if cantidad < 1:
                                raise ValueError
                        except (ValueError, TypeError):
                            errores.append(f'Cantidad inválida para "{producto.nombre}".')
                            continue
                        if producto.stock <= 0:
                            errores.append(f'"{producto.nombre}" no tiene stock disponible.')
                        elif cantidad > producto.stock:
                            errores.append(
                                f'Stock insuficiente para "{producto.nombre}": '
                                f'solo hay {producto.stock} unidad(es) disponibles.'
                            )
                        else:
                            items_validated.append((producto, cantidad))

                    if errores:
                        for e in errores:
                            form.add_error(None, e)
                    else:
                        # Todo válido: guardar préstamo e ítems
                        prestamo = form.save()
                        for producto, cantidad in items_validated:
                            ItemPrestamo.objects.create(
                                prestamo=prestamo,
                                producto=producto,
                                cantidad=cantidad,
                            )
                            producto.stock -= cantidad
                            producto.save(update_fields=['stock'])
                        messages.success(request, 'Préstamo registrado exitosamente.')
                        return redirect('prestamo')

    else:
        form = PrestamoForm()

    prestamos = Prestamo.objects.prefetch_related('items__producto').all()
    productos = Producto.objects.all().order_by('nombre')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    usuarios = User.objects.all().order_by('username')

    total_prestamos     = prestamos.count()
    prestamos_activos   = prestamos.filter(estado='activo').count()
    prestamos_devueltos = prestamos.filter(estado='devuelto').count()
    prestamos_vencidos  = prestamos.filter(estado='vencido').count()

    return render(request, 'prestamo.html', {
        'form':                form,
        'prestamos':           prestamos,
        'productos':           productos,
        'usuarios':            usuarios,
        'total_prestamos':     total_prestamos,
        'prestamos_activos':   prestamos_activos,
        'prestamos_devueltos': prestamos_devueltos,
        'prestamos_vencidos':  prestamos_vencidos,
    })


def prestamo_api(request, pk):
    """Endpoint AJAX usado por el modal de devoluciones para buscar un préstamo."""
    try:
        p = Prestamo.objects.prefetch_related('items__producto').get(pk=pk)
    except Prestamo.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)

    data = {
        'id':            p.pk,
        'usuario':       str(p.usuario),
        'estado':        p.estado,
        'observaciones': p.observaciones,
        'fecha_prestamo': p.fecha_prestamo.isoformat(),
        'items': [
            {
                'id':       item.pk,
                'devuelto': item.devuelto,
                'cantidad': item.cantidad,
                'producto': {
                    'id':         item.producto.pk,
                    'nombre':     item.producto.nombre,
                    'codigo_sku': item.producto.codigo_sku,
                    'stock':      item.producto.stock,
                }
            }
            for item in p.items.all()
        ]
    }
    return JsonResponse(data)