# prestamo/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
import datetime

from .forms import PrestamoForm
from .models import Prestamo, ItemPrestamo
from inventario.models import Producto


def _marcar_vencidos():
    hoy = timezone.localdate()
    return Prestamo.objects.filter(
        estado__in=['activo', 'parcial'],
        fecha_vencimiento__lt=hoy,
    ).update(estado='vencido')


# ── Vista portal de usuario ────────────────────────────────────────────────
def prestamo_usuario_view(request):
    """Portal personal: el usuario ve sus propios préstamos y puede solicitar."""
    doc = request.session.get('usuario_documento')
    if not doc:
        return redirect('login')

    _marcar_vencidos()

    from usuario.models import Usuario
    usuario = get_object_or_404(Usuario, numero_documento=doc)

    # Filtrar préstamos por el documento del usuario (campo 'usuario' en Prestamo)
    all_prestamos = (
        Prestamo.objects
        .prefetch_related('items__producto')
        .filter(usuario=doc)
        .order_by('-fecha_prestamo')
    )

    hoy = timezone.localdate()

    total_prestamos       = all_prestamos.count()
    total_activos         = all_prestamos.filter(estado='activo').count()
    vencidos_count        = all_prestamos.filter(estado='vencido').count()
    pendientes_aprobacion = 0  # reservado para flujo de aprobación futuro

    proximos_vencer = all_prestamos.filter(
        estado__in=['activo', 'parcial'],
        fecha_vencimiento__lte=hoy + timezone.timedelta(days=3),
        fecha_vencimiento__gte=hoy,
    ).count()

    productos_disponibles = Producto.objects.filter(stock__gt=0).order_by('nombre')

    return render(request, 'prestamo_usuario.html', {
        'usuario':               usuario,
        'all_prestamos':         all_prestamos,
        'total_prestamos':       total_prestamos,
        'total_activos':         total_activos,
        'vencidos_count':        vencidos_count,
        'pendientes_aprobacion': pendientes_aprobacion,
        'proximos_vencer':       proximos_vencer,
        'productos_disponibles': productos_disponibles,
    })


def prestamos_view(request):
    _marcar_vencidos()

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # ── Cancelar préstamo ──────────────────────────────────────────────
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

        # ── Editar préstamo ────────────────────────────────────────────────
        elif accion == 'editar':
            prestamo = get_object_or_404(Prestamo, pk=request.POST.get('prestamo_pk'))
            prestamo.estado         = request.POST.get('estado', prestamo.estado)
            prestamo.observaciones  = request.POST.get('observaciones', '')
            prestamo.nombre_usuario = request.POST.get('nombre_usuario', '')

            usuario_str = request.POST.get('usuario', '').strip()
            if usuario_str:
                prestamo.usuario = usuario_str

            fv = request.POST.get('fecha_vencimiento', '').strip()
            try:
                prestamo.fecha_vencimiento = datetime.date.fromisoformat(fv) if fv else None
            except ValueError:
                prestamo.fecha_vencimiento = None

            hme = request.POST.get('hora_max_entrega', '').strip()
            try:
                prestamo.hora_max_entrega = datetime.time.fromisoformat(hme) if hme else None
            except ValueError:
                prestamo.hora_max_entrega = None

            prestamo.save()
            messages.success(request, f'Préstamo #{prestamo.pk} actualizado.')
            return redirect('prestamo')

        # ── Eliminar préstamo ──────────────────────────────────────────────
        elif accion == 'eliminar':
            prestamo = get_object_or_404(Prestamo, pk=request.POST.get('prestamo_pk'))
            for item in prestamo.items.filter(devuelto=False):
                item.producto.stock += item.cantidad
                item.producto.save()
            prestamo.delete()
            messages.success(request, 'Préstamo eliminado correctamente.')
            return redirect('prestamo')

        # ── Devolver ítem individual ───────────────────────────────────────
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

        # ── Crear nuevo préstamo ───────────────────────────────────────────
        else:
            form = PrestamoForm(request.POST)
            if form.is_valid():
                producto_ids = request.POST.getlist('producto[]')
                cantidades   = request.POST.getlist('cantidad[]')

                items_raw = [
                    (pid, qty)
                    for pid, qty in zip(producto_ids, cantidades)
                    if pid
                ]

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
                        prestamo = form.save(commit=False)
                        prestamo.nombre_usuario = request.POST.get('nombre_usuario', '')

                        fv = request.POST.get('fecha_vencimiento', '').strip()
                        try:
                            prestamo.fecha_vencimiento = datetime.date.fromisoformat(fv) if fv else None
                        except ValueError:
                            prestamo.fecha_vencimiento = None

                        hme = request.POST.get('hora_max_entrega', '').strip()
                        try:
                            prestamo.hora_max_entrega = datetime.time.fromisoformat(hme) if hme else None
                        except ValueError:
                            prestamo.hora_max_entrega = None

                        prestamo.save()

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

    # ── GET: filtros ───────────────────────────────────────────────────────
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
            estado__in=['activo', 'parcial', 'vencido'],
        )

    productos = Producto.objects.filter(stock__gt=0).order_by('nombre')

    from usuario.models import Usuario
    usuarios_sistema = Usuario.objects.all().order_by('nombre_completo')

    # JSON para el wizard
    import json
    usuarios_json = json.dumps([
        {'doc': u.numero_documento, 'nombre': u.nombre_completo, 'tipo': u.tipo_documento}
        for u in usuarios_sistema
    ])
    productos_json = json.dumps([
        {'pk': p.pk, 'nombre': p.nombre, 'sku': p.codigo_sku, 'stock': p.stock}
        for p in productos
    ])

    total_prestamos     = Prestamo.objects.count()
    prestamos_activos   = Prestamo.objects.filter(estado='activo').count()
    prestamos_devueltos = Prestamo.objects.filter(estado='devuelto').count()
    prestamos_vencidos  = Prestamo.objects.filter(estado='vencido').count()

    hoy = timezone.localdate()
    proximos_vencer = Prestamo.objects.filter(
        estado__in=['activo', 'parcial'],
        fecha_vencimiento__lte=hoy + timezone.timedelta(days=3),
        fecha_vencimiento__gte=hoy,
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


# ── Vista para solicitud de préstamo desde el portal de usuario ────────────
def usuario_solicitar_prestamo(request):
    """Permite a un usuario autenticado solicitar un préstamo desde su portal."""
    if request.method != 'POST':
        return redirect('prestamo_usuario')

    from usuario.models import Usuario

    # Clave correcta de sesión
    doc = request.session.get('usuario_documento')
    if not doc:
        messages.error(request, 'Debes iniciar sesión para solicitar un préstamo.')
        return redirect('login')

    try:
        usuario = Usuario.objects.get(numero_documento=doc)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('login')

    producto_ids = request.POST.getlist('producto[]')
    cantidades   = request.POST.getlist('cantidad[]')
    fecha_str    = request.POST.get('fecha_devolucion_estimada', '').strip()
    motivo       = request.POST.get('motivo', '').strip()

    items_raw = [
        (pid, qty)
        for pid, qty in zip(producto_ids, cantidades)
        if pid
    ]

    if not items_raw:
        messages.error(request, 'Debes seleccionar al menos un producto.')
        return redirect('prestamo_usuario')

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
            messages.error(request, e)
        return redirect('prestamo_usuario')

    prestamo = Prestamo()
    prestamo.usuario        = doc
    prestamo.nombre_usuario = usuario.nombre_completo
    prestamo.observaciones  = motivo
    prestamo.estado         = 'activo'

    try:
        prestamo.fecha_vencimiento = datetime.date.fromisoformat(fecha_str) if fecha_str else None
    except ValueError:
        prestamo.fecha_vencimiento = None

    prestamo.save()

    for producto, cantidad in items_validated:
        ItemPrestamo.objects.create(
            prestamo=prestamo,
            producto=producto,
            cantidad=cantidad,
        )
        producto.stock -= cantidad
        producto.save(update_fields=['stock'])

    messages.success(request, f'Solicitud de préstamo #{prestamo.pk} registrada exitosamente.')
    return redirect('prestamo_usuario')


def prestamo_api(request, pk):
    try:
        p = Prestamo.objects.prefetch_related('items__producto').get(pk=pk)
    except Prestamo.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)

    data = {
        'id':                p.pk,
        'usuario':           str(p.usuario),
        'nombre_usuario':    p.nombre_usuario,
        'estado':            p.estado,
        'observaciones':     p.observaciones,
        'fecha_prestamo':    p.fecha_prestamo.isoformat(),
        'fecha_vencimiento': p.fecha_vencimiento.isoformat() if p.fecha_vencimiento else None,
        'hora_max_entrega':  p.hora_max_entrega.strftime('%H:%M') if p.hora_max_entrega else None,
        'dias_restantes':    p.dias_restantes,
        'urgencia':          p.urgencia,
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