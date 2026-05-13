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


# ── 1. No hay signals de estado porque Devolucion ya no mantiene campo de estado ─────────────────
# Este archivo permanece para referencia, pero hoy no aplica lógica de transición.

# ── 2. Limpiar al eliminar una devolución ─────────────────────────────────
@receiver(post_delete, sender=Devolucion)
def revertir_al_eliminar(sender, instance, **kwargs):
    """
    Si la devolución fue aplicada (stock restaurado) y se elimina,
    revertir el stock para mantener consistencia.
    """
    if getattr(instance, '_aplicada', False):
        for item in instance.items.select_related('producto'):
            item.producto.stock = max(0, item.producto.stock - item.cantidad)
            item.producto.save(update_fields=['stock', 'actualizado_en'])
            item.devuelto = False
            item.save(update_fields=['devuelto'])

        try:
            instance.prestamo.actualizar_estado()
        except Exception:
            pass