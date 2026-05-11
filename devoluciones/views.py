# devoluciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Devolucion
from prestamo.models import Prestamo, ItemPrestamo
from common.mixins import sesion_requerida   


@sesion_requerida 
def devoluciones_view(request):
    edit_id = None

    if request.method == 'POST':
        action = request.POST.get('action', 'crear')

        if action == 'crear':
            prestamo_id      = request.POST.get('prestamo_id', '').strip()
            motivo           = request.POST.get('motivo', '').strip()
            devolucion_total = request.POST.get('devolucion_total', 'true') == 'true'
            motivo_requerido = request.POST.get('motivo_requerido', 'true') == 'true'
            items_ids        = request.POST.getlist('items')

            errores = []
            if not prestamo_id:
                errores.append('No se indicó el préstamo.')

            # El motivo solo es obligatorio en devoluciones parciales
            if motivo_requerido and len(motivo) < 10:
                errores.append('El motivo debe tener al menos 10 caracteres.')

            if not items_ids:
                errores.append('Debes seleccionar al menos un ítem.')

            prestamo = None
            if prestamo_id:
                try:
                    prestamo = Prestamo.objects.get(pk=prestamo_id)
                    if prestamo.fecha_vencimiento and prestamo.fecha_vencimiento < timezone.localdate():
                        errores.append('No se puede devolver un préstamo con fecha de vencimiento en el pasado.')
                except Prestamo.DoesNotExist:
                    errores.append('Préstamo no encontrado.')

            if errores:
                for e in errores:
                    messages.error(request, e)
            else:
                prestamo   = get_object_or_404(Prestamo, pk=prestamo_id)
                devolucion = Devolucion.objects.create(
                    prestamo=prestamo,
                    motivo=motivo,
                    devolucion_total=devolucion_total,
                )
                items = ItemPrestamo.objects.filter(pk__in=items_ids, prestamo=prestamo)
                devolucion.items.set(items)

                # Recoger cantidades parciales por ítem
                cantidades = {}
                for item in items:
                    key = f'cantidad_{item.pk}'
                    try:
                        cant = int(request.POST.get(key, item.cantidad))
                        cantidades[item.pk] = max(1, min(cant, item.cantidad))
                    except (ValueError, TypeError):
                        cantidades[item.pk] = item.cantidad

                devolucion.aplicar(cantidades=cantidades)
                messages.success(request, 'Devolución registrada exitosamente.')
                return redirect('devoluciones')

        elif action == 'editar':
            pk           = request.POST.get('devolucion_id')
            instancia    = get_object_or_404(Devolucion, pk=pk)

            # No hay estado que editar, solo motivo
            messages.info(request, f'Devolución #{pk} no editable.')
            return redirect('devoluciones')

    devoluciones = Devolucion.objects.select_related('prestamo').prefetch_related('items__producto').all()

    # Préstamos que aún tienen ítems pendientes de devolución
    prestamos_activos = (
        Prestamo.objects
        .filter(estado__in=['activo', 'parcial', 'vencido'])
        .prefetch_related('items__producto')
        .order_by('-fecha_prestamo')
    )

    return render(request, 'devoluciones.html', {
        'edit_id':           edit_id,
        'devoluciones':      devoluciones,
        'prestamos_activos': prestamos_activos,
    })