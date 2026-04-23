# prestamo/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .forms import PrestamoForm
from .models import Prestamo, ItemPrestamo
from inventario.models import Producto


def _marcar_vencidos():
    hoy = timezone.localdate()
    vencidos = Prestamo.objects.filter(
        estado__in=['activo', 'parcial'],
        fecha_vencimiento__lt=hoy
    )
    count = vencidos.update(estado='vencido')
    return count


def _get_context_base():
    """Datos comunes que siempre se necesitan en la vista (GET y POST fallido)."""
    from usuario.models import Usuario
    usuarios_sistema = list(
        Usuario.objects.all().order_by('nombre_completo').values(
            'numero_documento', 'nombre_completo', 'tipo_documento'
        )
    )
    productos = Producto.objects.filter(stock__gt=0).order_by('nombre')

    # Serializar usuarios de forma segura para el wizard
    usuarios_json = json.dumps([
        {
            'doc':    u['numero_documento'],
            'nombre': u['nombre_completo'],
            'tipo':   u['tipo_documento'],
        }
        for u in usuarios_sistema
    ], ensure_ascii=False)

    productos_json = json.dumps([
        {
            'pk':     p.pk,
            'sku':    p.codigo_sku,
            'nombre': p.nombre,
            'stock':  p.stock,
        }
        for p in productos
    ], ensure_ascii=False)

    return usuarios_sistema, productos, usuarios_json, productos_json


def prestamos_view(request):
    _marcar_vencidos()

    if request.method == 'POST':
        accion = request.POST.get('accion')

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

        elif accion == 'editar':
            prestamo = get_object_or_404(Prestamo, pk=request.POST.get('prestamo_pk'))
            prestamo.estado = request.POST.get('estado', prestamo.estado)
            prestamo.observaciones = request.POST.get('observaciones', '')
            usuario_str = request.POST.get('usuario', '').strip()
            nombre_str  = request.POST.get('nombre_usuario', '').strip()
            if usuario_str:
                prestamo.usuario = usuario_str
            prestamo.nombre_usuario = nombre_str
            fecha_str = request.POST.get('fecha_vencimiento', '').strip()
            if fecha_str:
                from datetime import date
                try:
                    prestamo.fecha_vencimiento = date.fromisoformat(fecha_str)
                except ValueError:
                    messages.error(request, 'Formato de fecha inválido.')
                    return redirect('prestamo')
            else:
                prestamo.fecha_vencimiento = None
            prestamo.save()
            messages.success(request, f'Préstamo #{prestamo.pk} actualizado.')
            return redirect('prestamo')

        elif accion == 'eliminar':
            prestamo = get_object_or_404(Prestamo, pk=request.POST.get('prestamo_pk'))
            for item in prestamo.items.filter(devuelto=False):
                item.producto.stock += item.cantidad
                item.producto.save()
            prestamo.delete()
            messages.success(request, 'Préstamo eliminado correctamente.')
            return redirect('prestamo')

        elif accion == 'devolver_item':
            item = get_object_or_404(ItemPrestamo, pk=request.POST.get('item_pk'))
            cantidad = int(request.POST.get('cantidad_devuelta', item.cantidad))
            cantidad = max(1, min(cantidad, item.cantidad))
            item.producto.stock += cantidad
            item.producto.save()
            item.devuelto = True
            item.save()
            prestamo = item.prestamo
            if not prestamo.items.filter(devuelto=False).exists():
                prestamo.estado = 'devuelto'
                prestamo.save()
            messages.success(request, f'"{item.producto.nombre}" devuelto correctamente.')
            return redirect('prestamo')

        else:
            form = PrestamoForm(request.POST)
            if form.is_valid():
                producto_ids = request.POST.getlist('producto[]')
                cantidades   = request.POST.getlist('cantidad[]')
                items_raw = [(pid, qty) for pid, qty in zip(producto_ids, cantidades) if pid]

                if not items_raw:
                    form.add_error(None, 'Debes seleccionar al menos una herramienta.')
                else:
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
                                f'solo hay {producto.stock} disponibles.'
                            )
                        else:
                            items_validated.append((producto, cantidad))

                    if errores:
                        for e in errores:
                            form.add_error(None, e)
                    else:
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

    # ── Filtros GET ──
    q          = request.GET.get('q', '').strip()
    estado_f   = request.GET.get('estado', '').strip()
    vencidos_f = request.GET.get('vencidos', '').strip()

    prestamos = Prestamo.objects.prefetch_related('items__producto').all()

    if q:
        prestamos = prestamos.filter(
            Q(usuario__icontains=q) |
            Q(nombre_usuario__icontains=q) |
            Q(items__producto__nombre__icontains=q)
        ).distinct()

    if estado_f:
        prestamos = prestamos.filter(estado=estado_f)

    if vencidos_f == '1':
        hoy = timezone.localdate()
        prestamos = prestamos.filter(
            fecha_vencimiento__lt=hoy,
            estado__in=['activo', 'parcial', 'vencido']
        )

    # ── Datos para el wizard — SIEMPRE se calculan ──
    usuarios_sistema, productos, usuarios_json, productos_json = _get_context_base()

    total_prestamos     = Prestamo.objects.count()
    prestamos_activos   = Prestamo.objects.filter(estado='activo').count()
    prestamos_devueltos = Prestamo.objects.filter(estado='devuelto').count()
    prestamos_vencidos  = Prestamo.objects.filter(estado='vencido').count()

    hoy = timezone.localdate()
    proximos_vencer = Prestamo.objects.filter(
        estado__in=['activo', 'parcial'],
        fecha_vencimiento__lte=hoy + timezone.timedelta(days=3),
        fecha_vencimiento__gte=hoy
    ).count()

    return render(request, 'prestamo.html', {
        'form':                form,
        'prestamos':           prestamos,
        'productos':           productos,
        'usuarios_sistema':    usuarios_sistema,
        'usuarios_json':       usuarios_json,
        'productos_json':      productos_json,
        'total_prestamos':     total_prestamos,
        'prestamos_activos':   prestamos_activos,
        'prestamos_devueltos': prestamos_devueltos,
        'prestamos_vencidos':  prestamos_vencidos,
        'proximos_vencer':     proximos_vencer,
        'filtro_q':            q,
        'filtro_estado':       estado_f,
        'filtro_vencidos':     vencidos_f,
    })


def prestamo_api(request, pk):
    try:
        p = Prestamo.objects.prefetch_related('items__producto').get(pk=pk)
    except Prestamo.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)

    hoy = timezone.localdate()
    data = {
        'id':               p.pk,
        'usuario':          str(p.usuario),
        'nombre_usuario':   p.nombre_usuario,
        'estado':           p.estado,
        'observaciones':    p.observaciones,
        'fecha_prestamo':   p.fecha_prestamo.isoformat(),
        'fecha_vencimiento': p.fecha_vencimiento.isoformat() if p.fecha_vencimiento else None,
        'dias_restantes':   p.dias_restantes,
        'urgencia':         p.urgencia,
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