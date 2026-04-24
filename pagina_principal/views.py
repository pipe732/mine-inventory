from django.shortcuts import render
from django.db.models import Sum, Max
from inventario.models import Producto, Categoria
from prestamo.models import Prestamo
from devoluciones.models import Devolucion


def dashboard_view(request):
    # ── Inventario ──
    total_productos  = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    # ── Préstamos ──
    prestamos_activos_count  = Prestamo.objects.filter(estado='activo').count()
    prestamos_vencidos_count = Prestamo.objects.filter(estado='vencido').count()
    prestamos_recientes      = Prestamo.objects.prefetch_related('items__producto').order_by('-fecha_prestamo')[:5]
    # ── Devoluciones ──
    devoluciones_pendientes_count = Devolucion.objects.filter(estado='pendiente').count()
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
        'total_productos':               total_productos,
        'total_categorias':              total_categorias,
        'prestamos_activos_count':       prestamos_activos_count,
        'prestamos_vencidos_count':      prestamos_vencidos_count,
        'devoluciones_pendientes_count': devoluciones_pendientes_count,
        'prestamos_recientes':           prestamos_recientes,
        'devoluciones_recientes':        devoluciones_recientes,
        'productos_recientes':           productos_recientes,
        'stock_por_categoria':           stock_por_categoria,
        'max_stock':                     max_stock,
    })


def home_usuario_view(request):
    from usuario.models import Usuario
    from django.utils import timezone

    usuario_id = request.session.get('usuario_id')
    usuario             = None
    all_prestamos       = []
    prestamos_activos   = []
    historial_reciente  = []
    total_prestamos     = 0
    vencidos_count      = 0

    if usuario_id:
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            nombre  = usuario.nombre_completo

            # Todos los préstamos del usuario, con sus ítems
            all_prestamos = (
                Prestamo.objects
                .prefetch_related('items__producto')
                .filter(nombre_usuario=nombre)
                .order_by('-fecha_prestamo')
            )

            total_prestamos = all_prestamos.count()

            # Activos y parciales (en curso)
            prestamos_activos = all_prestamos.filter(estado__in=['activo', 'parcial', 'vencido'])

            # Devueltos
            historial_reciente = all_prestamos.filter(estado='devuelto')

            # Alertas
            vencidos_count = all_prestamos.filter(estado='vencido').count()

        except Usuario.DoesNotExist:
            pass

    productos_disponibles = Producto.objects.filter(stock__gt=0).order_by('nombre')

    return render(request, 'home_usuario.html', {
        'usuario':                usuario,
        'all_prestamos':          all_prestamos,         # ← usado en la tabla
        'prestamos_activos':      prestamos_activos,     # ← para el stat card
        'historial_reciente':     historial_reciente,    # ← para el stat card
        'total_prestamos':        total_prestamos,
        'vencidos_count':         vencidos_count,
        'productos_disponibles':  productos_disponibles,
    })
