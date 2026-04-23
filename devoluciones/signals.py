# devoluciones/signals.py
"""
Signals para el módulo de devoluciones.

Conectar en devoluciones/apps.py dentro de ready():

    class DevolucionesConfig(AppConfig):
        name = 'devoluciones'

        def ready(self):
            import devoluciones.signals  # noqa: F401
"""
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from .models import Devolucion


# ── 1. Detectar cambio de estado y aplicar/revertir stock ─────────────────
@receiver(pre_save, sender=Devolucion)
def gestionar_stock_en_cambio_estado(sender, instance, **kwargs):
    """
    Compara el estado anterior con el nuevo y actúa en consecuencia:

    pendiente → aprobada  : no hace nada extra (aplicar() ya corrió al crear)
    pendiente → rechazada : revierte el stock (revertir())
    rechazada → aprobada  : aplica el stock de nuevo (aplicar())
    aprobada  → rechazada : revierte el stock (revertir())

    Las transiciones desde/hacia 'pendiente' en creación se manejan
    explícitamente en la vista con devolucion.aplicar().
    """
    if not instance.pk:
        # Objeto nuevo: no hay estado anterior
        return

    try:
        anterior = Devolucion.objects.get(pk=instance.pk)
    except Devolucion.DoesNotExist:
        return

    estado_anterior = anterior.estado
    estado_nuevo    = instance.estado

    # Sin cambio de estado: nada que hacer
    if estado_anterior == estado_nuevo:
        return

    TRANSICIONES_REVERTIR = {
        ('pendiente', 'rechazada'),
        ('aprobada',  'rechazada'),
    }
    TRANSICIONES_APLICAR = {
        ('rechazada', 'aprobada'),
    }

    if (estado_anterior, estado_nuevo) in TRANSICIONES_REVERTIR:
        instance.revertir()

    elif (estado_anterior, estado_nuevo) in TRANSICIONES_APLICAR:
        # Forzar _aplicada=False para que aplicar() pueda ejecutarse
        instance._aplicada = False
        instance.aplicar()


# ── 2. Limpiar al eliminar una devolución ─────────────────────────────────
@receiver(post_delete, sender=Devolucion)
def revertir_al_eliminar(sender, instance, **kwargs):
    """
    Si la devolución fue aplicada (stock restaurado) y se elimina,
    revertir el stock para mantener consistencia.
    """
    if instance._aplicada:
        # Los ítems M2M ya fueron eliminados con la devolución,
        # así que necesitamos revertir manualmente con los datos del objeto.
        # Nota: post_delete aún tiene acceso al objeto en memoria.
        for item in instance.items.select_related('producto'):
            item.producto.stock = max(0, item.producto.stock - item.cantidad)
            item.producto.save(update_fields=['stock', 'actualizado_en'])
            item.devuelto = False
            item.save(update_fields=['devuelto'])

        try:
            instance.prestamo.actualizar_estado()
        except Exception:
            pass