from django.shortcuts import render, redirect
from django.db.models import Sum, Max
from inventario.models import Producto, Categoria
from django.utils import timezone
from prestamo.models import Prestamo
from devoluciones.models import Devolucion
from django.http import JsonResponse
from django.utils import timezone
#from common.mixins import sesion_requerida 

#@sesion_requerida     
def dashboard_view(request):
    """Home del administrador — solo accesible por admins."""
    # Validar que el usuario sea administrador
    rol = (request.session.get('usuario_rol') or '').strip().lower()
    if rol not in ('administrador', 'admin'):
        return redirect('home_usuario')
    
    # ── Inventario ──
    total_productos  = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    # ── Préstamos ──
    prestamos_activos_count   = Prestamo.objects.filter(estado='activo').count()
    prestamos_vencidos_count  = Prestamo.objects.filter(estado='vencido').count()
    prestamos_recientes       = Prestamo.objects.prefetch_related('items__producto').order_by('-fecha_prestamo')[:5]
    # ── Devoluciones ──
    devoluciones_pendientes_count = Devolucion.objects.count()
    devoluciones_recientes        = Devolucion.objects.select_related('prestamo').order_by('-fecha_creacion')[:5]
    # ── Stock por categoría ──
    stock_por_categoria = (
        Categoria.objects
        .annotate(total_stock=Sum('productos__stock'))
        .filter(total_stock__isnull=False)
        .order_by('-total_stock')
    )
    max_stock = stock_por_categoria.aggregate(m=Max('total_stock'))['m'] or 1
    # ── Productos recientes ──
    productos_recientes = Producto.objects.select_related('categoria').order_by('-actualizado_en')[:8]

    return render(request, 'pagina_principal.html', {
        'total_productos':                total_productos,
        'total_categorias':               total_categorias,
        'prestamos_activos_count':        prestamos_activos_count,
        'prestamos_vencidos_count':       prestamos_vencidos_count,
        'devoluciones_pendientes_count':  devoluciones_pendientes_count,
        'prestamos_recientes':            prestamos_recientes,
        'devoluciones_recientes':         devoluciones_recientes,
        'productos_recientes':            productos_recientes,
        'stock_por_categoria':            stock_por_categoria,
        'max_stock':                      max_stock,
    })


def home_usuario_view(request):
    """Home del usuario — muestra sus propios préstamos."""
    from usuario.models import Usuario
    from django.utils import timezone

    # ← CORRECCIÓN: la sesión guarda 'usuario_documento', no 'usuario_id'
    doc = request.session.get('usuario_documento')
    if not doc:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(numero_documento=doc)
    except Usuario.DoesNotExist:
        return redirect('login')

    # Todos los préstamos del usuario identificado por su documento
    all_prestamos = (
        Prestamo.objects
        .prefetch_related('items__producto')
        .filter(usuario=doc)
        .order_by('-fecha_prestamo')
    )

    total_prestamos    = all_prestamos.count()
    prestamos_activos  = all_prestamos.filter(estado__in=['activo', 'parcial'])
    historial_reciente = all_prestamos.filter(estado='devuelto')
    vencidos_count     = all_prestamos.filter(estado='vencido').count()

    productos_disponibles = Producto.objects.filter(stock__gt=0).order_by('nombre')

    # Alertas de stock bajo
    alertas_stock = list(Producto.objects.filter(stock__lt=5).values_list('nombre', 'stock'))
    hay_alertas = len(alertas_stock) > 0

    return render(request, 'home_usuario.html', {
        'usuario':               usuario,
        'all_prestamos':         all_prestamos,
        'prestamos_activos':     prestamos_activos,
        'historial_reciente':    historial_reciente,
        'total_prestamos':       total_prestamos,
        'vencidos_count':        vencidos_count,
        'productos_disponibles': productos_disponibles,
        'alertas_stock':         alertas_stock,
        'hay_alertas':           hay_alertas,
    })
# ─────────────────────────────────────────────────────────────
#  NOTIFICACIONES JSON — agregar a pagina_principal/views.py
#  Importar JsonResponse si no está: from django.http import JsonResponse
# ─────────────────────────────────────────────────────────────
def notificaciones_json(request):
    """Devuelve notificaciones activas para el usuario en sesión.

    Acepta ?page= para filtrar por contexto:
      - page=principal  → solo préstamos vencidos
      - page=inventario → solo herramientas con stock < 5 unidades
      - (sin param)     → todas las notificaciones
    """
    doc = request.session.get('usuario_documento')
    rol = (request.session.get('usuario_rol') or '').strip().lower()
    if not doc:
        return JsonResponse({'items': [], 'total': 0})

    hoy      = timezone.localdate()
    proximos = hoy + timezone.timedelta(days=3)
    items    = []

    # Parámetro de contexto de página
    page = (request.GET.get('page') or '').strip().lower()

    # ── Para admin/administrador: notificaciones globales ────────
    if rol in ('administrador', 'admin'):

        # ─── PRÉSTAMOS ACTIVOS ───
        if page not in ('principal', 'inventario'):
            activos = Prestamo.objects.filter(estado__in=['activo', 'parcial']).count()
            if activos:
                items.append({
                    'tipo':  'activo',
                    'icono': 'box-seam',
                    'color': '#1D9E75',
                    'titulo': f'{activos} préstamo{"s" if activos != 1 else ""} activo{"s" if activos != 1 else ""}',
                    'desc':  'Préstamos en curso',
                    'url':   '/prestamo/?estado=activo',
                })

        # ─── SOLICITUDES PENDIENTES ───
        # Se omiten las notificaciones generales de préstamos pendientes de aprobación
        # para evitar alertas redundantes que no se desean mostrar en la campana.

        # ─── PRÉSTAMOS VENCIDOS (en principal y en "todas") ───
        if page != 'inventario':
            venc = Prestamo.objects.filter(estado='vencido').count()
            if venc:
                items.append({
                    'tipo':  'vencido',
                    'icono': 'exclamation-circle',
                    'color': '#98473E',
                    'titulo': f'{venc} préstamo{"s" if venc != 1 else ""} vencido{"s" if venc != 1 else ""}',
                    'desc':  'Requieren atención inmediata',
                    'url':   '/prestamo/?estado=vencido',
                })

            # También incluir préstamos activos/parciales cuya fecha ya pasó
            # pero cuyo estado no se actualizó a "vencido" aún
            venc_no_marcados = Prestamo.objects.filter(
                estado__in=['activo', 'parcial'],
                fecha_vencimiento__lt=hoy,
            ).count()
            if venc_no_marcados:
                items.append({
                    'tipo':  'vencido_no_marcado',
                    'icono': 'alarm',
                    'color': '#98473E',
                    'titulo': f'{venc_no_marcados} préstamo{"s" if venc_no_marcados != 1 else ""} con fecha vencida',
                    'desc':  'Activos pero ya pasaron su fecha límite',
                    'url':   '/prestamo/',
                })

        # ─── PRÓXIMOS A VENCER ───
        if page != 'inventario':
            prox = Prestamo.objects.filter(
                estado__in=['activo', 'parcial'],
                fecha_vencimiento__lte=proximos,
                fecha_vencimiento__gte=hoy,
            ).count()
            if prox:
                items.append({
                    'tipo':  'proximo',
                    'icono': 'alarm',
                    'color': '#c4900a',
                    'titulo': f'{prox} préstamo{"s" if prox != 1 else ""} próximo{"s" if prox != 1 else ""} a vencer',
                    'desc':  'Vencen en los próximos 3 días',
                    'url':   '/prestamo/?vencidos=1',
                })

        # ─── DEVOLUCIONES ───
        if page not in ('principal', 'inventario'):
            devs = Devolucion.objects.count()
            if devs:
                items.append({
                    'tipo':  'devolucion',
                    'icono': 'arrow-counterclockwise',
                    'color': '#094D92',
                    'titulo': f'{devs} devolución{"es" if devs != 1 else ""} registrada{"s" if devs != 1 else ""}',
                    'desc':  'Revisar en módulo de devoluciones',
                    'url':   '/devoluciones/',
                })

        # ─── STOCK BAJO (en inventario y en "todas") ───
        if page != 'principal':
            productos_bajo = list(
                Producto.objects.filter(stock__gt=0, stock__lt=5)
                .values_list('nombre', 'stock')
                .order_by('stock')
            )
            if productos_bajo:
                for nombre, stock in productos_bajo:
                    items.append({
                        'tipo':  'stock_bajo',
                        'icono': 'exclamation-circle',
                        'color': '#c4900a',
                        'titulo': f'{nombre}',
                        'desc':  f'Quedan {stock} unidad{"es" if stock != 1 else ""}',
                        'url':   '/inventario/',
                    })

            # Stock crítico (sin stock) — también en inventario
            productos_sin = list(
                Producto.objects.filter(stock=0)
                .values_list('nombre', flat=True)
                .order_by('nombre')
            )
            if productos_sin:
                for nombre in productos_sin:
                    items.append({
                        'tipo':  'stock',
                        'icono': 'box-seam',
                        'color': '#71816D',
                        'titulo': f'{nombre}',
                        'desc':  'Sin stock — verificar inventario',
                        'url':   '/inventario/',
                    })

    else:
        # ── Para usuario normal: solo sus préstamos ──────────────

        # Sus préstamos vencidos
        venc_u = Prestamo.objects.filter(usuario=doc, estado='vencido').count()
        if venc_u:
            items.append({
                'tipo':  'vencido',
                'icono': 'exclamation-circle',
                'color': '#98473E',
                'titulo': f'{venc_u} préstamo{"s" if venc_u != 1 else ""} vencido{"s" if venc_u != 1 else ""}',
                'desc':  'Contacta al administrador',
                'url':   '/prestamo/usuario/',
            })

        # Sus préstamos próximos a vencer
        prox_u = Prestamo.objects.filter(
            usuario=doc,
            estado__in=['activo', 'parcial'],
            fecha_vencimiento__lte=proximos,
            fecha_vencimiento__gte=hoy,
        ).count()
        if prox_u:
            items.append({
                'tipo':  'proximo',
                'icono': 'alarm',
                'color': '#c4900a',
                'titulo': f'{prox_u} préstamo{"s" if prox_u != 1 else ""} vence{"n" if prox_u != 1 else ""} pronto',
                'desc':  'En los próximos 3 días',
                'url':   '/prestamo/usuario/',
            })

        # Solicitudes pendientes de aprobación propias
        # No se generan notificaciones en la campana para solicitudes pendientes.

    return JsonResponse({'items': items, 'total': len(items)})