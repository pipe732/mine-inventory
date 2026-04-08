from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from .models import ReporteHistorial
from .generators import generar_reporte


MODULOS = [
    ('inventario',     'Inventario',     'bi-boxes',          'Productos, SKU, stock y categorías'),
    ('prestamos',      'Préstamos',      'bi-arrow-left-right','Registro de préstamos y estados'),
    ('devoluciones',   'Devoluciones',   'bi-arrow-counterclockwise', 'Devoluciones y motivos'),
    ('mantenimiento',  'Mantenimiento',  'bi-tools',          'Estado de herramientas'),
    ('almacenamiento', 'Almacenamiento', 'bi-building',       'Almacenes y estantes'),
    ('usuarios',       'Usuarios',       'bi-people',         'Usuarios y roles del sistema'),
]


def reportes_view(request):
    historial = ReporteHistorial.objects.all()[:50]
    return render(request, 'reportes.html', {
        'modulos':   MODULOS,
        'historial': historial,
    })


@require_POST
def generar_reporte_view(request):
    modulo  = request.POST.get('modulo', '').strip()
    formato = request.POST.get('formato', '').strip()

    if not modulo or not formato:
        return JsonResponse({'error': 'Módulo y formato son requeridos.'}, status=400)

    try:
        buf, content_type, filename, total = generar_reporte(modulo, formato)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error al generar el reporte: {e}'}, status=500)

    # Guardar en historial
    import json
    from django.utils import timezone

    generado_por = request.session.get('usuario_nombre', 'Sistema')
    registro = ReporteHistorial.objects.create(
        modulo          = modulo,
        formato         = formato,
        nombre_archivo  = filename,
        generado_por    = generado_por,
        total_registros = total,
    )

    LABELS = {
        'inventario': 'Inventario', 'prestamos': 'Préstamos',
        'devoluciones': 'Devoluciones', 'mantenimiento': 'Mantenimiento',
        'almacenamiento': 'Almacenamiento', 'usuarios': 'Usuarios',
    }

    historial_data = json.dumps({
        'id':          registro.pk,
        'modulo_label': LABELS.get(modulo, modulo.capitalize()),
        'formato':     formato,
        'filename':    filename,
        'generado_por': generado_por,
        'total':       total,
        'fecha':       registro.fecha_generado.strftime('%d/%m/%Y %H:%M'),
    })

    response = HttpResponse(buf.read(), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['X-Historial'] = historial_data
    return response