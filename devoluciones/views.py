# devoluciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Devolucion
from prestamo.models import Prestamo, ItemPrestamo
from common.mixins import sesion_requerida   


@sesion_requerida 
def devoluciones_view(request):
    edit_id = None

    if request.method == 'POST':
        action = request.POST.get('action', 'crear')

        # ─────────────────────────────────────────────
        # CREAR devolución
        # ─────────────────────────────────────────────
        if action == 'crear':
            prestamo_id      = request.POST.get('prestamo_id', '').strip()
            motivo           = request.POST.get('motivo', '').strip()
            devolucion_total = request.POST.get('devolucion_total', 'true') == 'true'
            motivo_requerido = request.POST.get('motivo_requerido', 'false') == 'true'
            items_ids        = request.POST.getlist('items')

            errores = []
            if not prestamo_id:
                errores.append('No se indicó el préstamo.')
            if motivo_requerido and len(motivo) < 5:
                errores.append('El motivo debe tener al menos 5 caracteres.')
            if not items_ids:
                errores.append('Debes seleccionar al menos un ítem.')

            if errores:
                for e in errores:
                    messages.error(request, e)
            else:
                prestamo = get_object_or_404(Prestamo, pk=prestamo_id)

                # Evitar duplicar devoluciones pendientes sobre los mismos ítems
                items_qs = ItemPrestamo.objects.filter(pk__in=items_ids, prestamo=prestamo)
                ya_en_proceso = Devolucion.objects.filter(
                    estado='pendiente',
                    items__in=items_qs
                ).distinct().exists()

                if ya_en_proceso:
                    messages.warning(
                        request,
                        'Uno o más ítems ya tienen una devolución pendiente. '
                        'Resuelve la existente antes de crear una nueva.'
                    )
                else:
                    devolucion = Devolucion.objects.create(
                        prestamo=prestamo,
                        motivo=motivo or '—',
                        devolucion_total=devolucion_total,
                        estado='pendiente',
                    )
                    devolucion.items.set(items_qs)
                    # Aplicar inmediatamente: marca ítems devueltos y ajusta stock
                    devolucion.aplicar()
                    messages.success(request, f'Devolución #{devolucion.pk} registrada y aplicada.')
                    return redirect('devoluciones')

        # ─────────────────────────────────────────────
        # EDITAR (cambiar estado: aprobada / rechazada)
        # ─────────────────────────────────────────────
        elif action == 'editar':
            pk           = request.POST.get('devolucion_id')
            nuevo_estado = request.POST.get('estado')
            instancia    = get_object_or_404(Devolucion, pk=pk)

            if nuevo_estado not in ('aprobada', 'rechazada'):
                messages.error(request, 'Estado no válido.')
                edit_id = pk
            elif instancia.estado == nuevo_estado:
                messages.info(request, f'La devolución ya estaba en estado "{nuevo_estado}".')
                return redirect('devoluciones')
            else:
                estado_anterior = instancia.estado

                # Si se rechaza una devolución que ya estaba aplicada (stock restaurado),
                # revertir el stock (descontar de nuevo)
                if nuevo_estado == 'rechazada' and estado_anterior == 'pendiente':
                    # La devolución se aplicó al crear → revertir
                    for item in instancia.items.select_related('producto'):
                        item.producto.stock -= item.cantidad
                        if item.producto.stock < 0:
                            item.producto.stock = 0
                        item.producto.save(update_fields=['stock', 'actualizado_en'])
                        # Revertir marca del ítem
                        item.devuelto = False
                        item.save(update_fields=['devuelto'])
                    # Recalcular estado del préstamo
                    instancia.prestamo.actualizar_estado()

                instancia.estado = nuevo_estado
                instancia.save(update_fields=['estado', 'fecha_actualizacion'])
                messages.success(request, f'Devolución #{pk} marcada como {nuevo_estado}.')
                return redirect('devoluciones')

        # ─────────────────────────────────────────────
        # ELIMINAR devolución
        # ─────────────────────────────────────────────
        elif action == 'eliminar':
            pk        = request.POST.get('devolucion_id')
            instancia = get_object_or_404(Devolucion, pk=pk)

            # Si la devolución estaba pendiente (ya aplicada), revertir stock
            if instancia.estado == 'pendiente':
                for item in instancia.items.select_related('producto'):
                    item.producto.stock -= item.cantidad
                    if item.producto.stock < 0:
                        item.producto.stock = 0
                    item.producto.save(update_fields=['stock', 'actualizado_en'])
                    item.devuelto = False
                    item.save(update_fields=['devuelto'])
                instancia.prestamo.actualizar_estado()

            instancia.delete()
            messages.success(request, f'Devolución #{pk} eliminada.')
            return redirect('devoluciones')

    # ─────────────────────────────────────────────
    # GET: listar devoluciones
    # ─────────────────────────────────────────────
    devoluciones = (
        Devolucion.objects
        .select_related('prestamo')
        .prefetch_related('items__producto')
        .all()
    )

    prestamos_activos = (
        Prestamo.objects
        .filter(estado__in=['activo', 'parcial', 'vencido'])
        .prefetch_related('items__producto')
        .order_by('-fecha_prestamo')
    )

    # Contadores para KPIs
    pendientes_count  = devoluciones.filter(estado='pendiente').count()
    aprobadas_count   = devoluciones.filter(estado='aprobada').count()
    rechazadas_count  = devoluciones.filter(estado='rechazada').count()

    return render(request, 'devoluciones.html', {
        'edit_id':           edit_id,
        'devoluciones':      devoluciones,
        'prestamos_activos': prestamos_activos,
        'pendientes_count':  pendientes_count,
        'aprobadas_count':   aprobadas_count,
        'rechazadas_count':  rechazadas_count,
        'total_count':       devoluciones.count(),
    })