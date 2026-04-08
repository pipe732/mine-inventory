# devoluciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Devolucion
from prestamo.models import Prestamo, ItemPrestamo


def devoluciones_view(request):
    edit_id = None

    if request.method == 'POST':
        action = request.POST.get('action', 'crear')

        if action == 'crear':
            prestamo_id      = request.POST.get('prestamo_id', '').strip()
            motivo           = request.POST.get('motivo', '').strip()
            devolucion_total = request.POST.get('devolucion_total', 'true') == 'true'
            items_ids        = request.POST.getlist('items')

            errores = []
            if not prestamo_id:
                errores.append('No se indicó el préstamo.')
            if len(motivo) < 10:
                errores.append('El motivo debe tener al menos 10 caracteres.')
            if not items_ids:
                errores.append('Debes seleccionar al menos un ítem.')

            if errores:
                for e in errores:
                    messages.error(request, e)
            else:
                prestamo   = get_object_or_404(Prestamo, pk=prestamo_id)
                devolucion = Devolucion.objects.create(
                    prestamo=prestamo,
                    motivo=motivo,
                    devolucion_total=devolucion_total,
                    estado='pendiente',
                )
                items = ItemPrestamo.objects.filter(pk__in=items_ids, prestamo=prestamo)
                devolucion.items.set(items)
                devolucion.aplicar()
                messages.success(request, 'Devolución registrada exitosamente.')
                return redirect('devoluciones')

        elif action == 'editar':
            pk           = request.POST.get('devolucion_id')
            nuevo_estado = request.POST.get('estado')
            instancia    = get_object_or_404(Devolucion, pk=pk)

            if nuevo_estado in ['pendiente', 'aprobada', 'rechazada']:
                instancia.estado = nuevo_estado
                instancia.save(update_fields=['estado', 'fecha_actualizacion'])
                messages.success(request, f'Devolución #{pk} actualizada correctamente.')
                return redirect('devoluciones')
            else:
                messages.error(request, 'Estado no válido.')
                edit_id = pk

    devoluciones = Devolucion.objects.select_related('prestamo').prefetch_related('items__producto').all()

    for d in devoluciones.filter(estado='rechazada'):
        messages.warning(
            request,
            f'⚠️ La devolución #{d.id} (Préstamo #{d.prestamo_id}) está marcada como rechazada.'
        )

    return render(request, 'devoluciones.html', {
        'edit_id':      edit_id,
        'devoluciones': devoluciones,
    })