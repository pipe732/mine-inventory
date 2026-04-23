from django.shortcuts import render
from django.db.models import Sum, Max
from inventario.models import Producto, Categoria
from prestamo.models import Prestamo
from devoluciones.models import Devolucion
#from common.mixins import sesion_requerida 

#@sesion_requerida     
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
        # KPI cards
        'total_productos':               total_productos,
        'total_categorias':              total_categorias,
        'prestamos_activos_count':       prestamos_activos_count,
        'prestamos_vencidos_count':      prestamos_vencidos_count,
        'devoluciones_pendientes_count': devoluciones_pendientes_count,
        # Tablas
        'prestamos_recientes':           prestamos_recientes,
        'devoluciones_recientes':        devoluciones_recientes,
        'productos_recientes':           productos_recientes,
        # Stock por categoría
        'stock_por_categoria':           stock_por_categoria,
        'max_stock':                     max_stock,
    })