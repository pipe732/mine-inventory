from django.shortcuts import render
from django.db.models import Sum
# Importaciones basadas estrictamente en tus archivos enviados
from inventario.models import Producto
from prestamo.models import Prestamo
from devoluciones.models import Devolucion

def dashboard_view(request):
    # 1. Resumen de Inventario (Modelo: Producto)
    total_productos = Producto.objects.count()
    # Sumamos el campo 'stock' de todos los productos
    unidades_totales = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    # Alerta si el campo 'stock' es menor o igual a 5
    alertas_stock = Producto.objects.filter(stock__lte=5).count()

    # 2. Resumen de Préstamos (Modelo: Prestamo)
    # Filtramos por el campo 'estado' con valor 'activo'
    prestamos_activos = Prestamo.objects.filter(estado='activo').count()

    # 3. Simulación de Movimientos (Modelo: Producto)
    # Como no hay tabla 'Movimientos', usamos los productos editados recientemente
    # Ordenamos por 'actualizado_en' que es tu campo real
    ultimas_actualizaciones = Producto.objects.all().order_by('-actualizado_en')[:5]

    # 4. Devoluciones Recientes (Modelo: Devolucion)
    recientes_dev = Devolucion.objects.all().order_by('-fecha_creacion')[:3]

    context = {
        'total_productos': total_productos,
        'unidades_totales': unidades_totales,
        'alertas_stock': alertas_stock,
        'prestamos_activos': prestamos_activos,
        'movimientos': ultimas_actualizaciones, # Pasamos los productos más recientes
        'devoluciones': recientes_dev,
    }

    return render(request, 'pagina_principal.html', context)