# devoluciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .forms import DevolucionForm, DevolucionEditForm
from .models import Devolucion


def devoluciones_view(request):
    """
    MINE-102: guardar nueva devolución (POST)
    MINE-104: listado de devoluciones
    MINE-105: detalle por fila (en template)
    """
    form_crear = DevolucionForm()
    edit_form  = None
    edit_id    = None

    if request.method == 'POST':
        action = request.POST.get('action', 'crear')

        # ── Crear nueva devolución ──
        if action == 'crear':
            form_crear = DevolucionForm(request.POST)
            if form_crear.is_valid():
                form_crear.save()
                messages.success(request, 'Devolución registrada exitosamente.')
                return redirect('devoluciones')

        # ── MINE-107 / MINE-109: Guardar edición ──
        elif action == 'editar':
            pk        = request.POST.get('devolucion_id')
            instancia = get_object_or_404(Devolucion, pk=pk)
            edit_form = DevolucionEditForm(request.POST, instance=instancia)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, f'Devolución #{pk} actualizada correctamente.')
                return redirect('devoluciones')
            else:
                edit_id = pk   # Para reabrir el modal con errores

    devoluciones = Devolucion.objects.all()

    # MINE-110: generar alerta si alguna devolución está en estado "rechazada"
    rechazadas = devoluciones.filter(estado='rechazada')
    if rechazadas.exists():
        for d in rechazadas:
            messages.warning(
                request,
                f'⚠️ La devolución #{d.id} (Orden: {d.numero_orden}) está marcada como dañada/rechazada.'
            )

    return render(request, 'devoluciones.html', {
        'form_crear': form_crear,
        'edit_form':  edit_form or DevolucionEditForm(),
        'edit_id':    edit_id,
        'devoluciones': devoluciones,
    })