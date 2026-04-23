# prestamo/signals.py
"""
Signals para el módulo de préstamos.

Conectar en prestamo/apps.py dentro de ready():

    class PrestamoConfig(AppConfig):
        name = 'prestamo'

        def ready(self):
            import prestamo.signals  # noqa: F401
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Prestamo, ItemPrestamo


# ── 1. Recalcular estado del préstamo cuando un ítem cambia ────────────────
@receiver(post_save, sender=ItemPrestamo)
def recalcular_estado_en_cambio_item(sender, instance, **kwargs):
    """
    Cada vez que un ItemPrestamo es guardado (devuelto=True/False, cantidad, etc.)
    se recalcula el estado del préstamo padre de forma automática.

    Se usa update_fields internamente para no disparar el signal de nuevo.
    """
    # Acceder al préstamo directamente para evitar query adicional
    try:
        prestamo = instance.prestamo
    except Prestamo.DoesNotExist:
        return

    # Calcular nuevo estado sin llamar a save() completo (evita bucle)
    items = prestamo.items.all()
    if not items.exists():
        return

    total     = items.count()
    devueltos = items.filter(devuelto=True).count()

    if devueltos == total:
        nuevo = 'devuelto'
    elif devueltos == 0:
        nuevo = 'vencido' if prestamo.esta_vencido else 'activo'
    else:
        nuevo = 'parcial'

    if prestamo.estado != nuevo:
        Prestamo.objects.filter(pk=prestamo.pk).update(
            estado=nuevo,
            fecha_actualizacion=timezone.now(),
        )


@receiver(post_delete, sender=ItemPrestamo)
def recalcular_estado_en_borrado_item(sender, instance, **kwargs):
    """Igual que el anterior, pero disparado cuando se elimina un ítem."""
    try:
        prestamo = instance.prestamo
    except Prestamo.DoesNotExist:
        return

    items = prestamo.items.all()
    if not items.exists():
        # Si no quedan ítems, dejar el estado como estaba
        return

    total     = items.count()
    devueltos = items.filter(devuelto=True).count()

    if devueltos == total:
        nuevo = 'devuelto'
    elif devueltos == 0:
        nuevo = 'vencido' if prestamo.esta_vencido else 'activo'
    else:
        nuevo = 'parcial'

    if prestamo.estado != nuevo:
        Prestamo.objects.filter(pk=prestamo.pk).update(
            estado=nuevo,
            fecha_actualizacion=timezone.now(),
        )


# ── 2. Auto-marcar vencidos al guardar cualquier Prestamo ──────────────────
@receiver(post_save, sender=Prestamo)
def auto_marcar_vencido(sender, instance, created, update_fields, **kwargs):
    """
    Si el préstamo tiene fecha_vencimiento pasada y no está devuelto,
    lo marca como 'vencido' automáticamente en el siguiente save.

    Se ignora cuando el save proviene del propio signal (update_fields=['estado',...])
    para evitar bucles infinitos.
    """
    # Evitar bucle: si el save ya viene de aquí (solo actualiza estado/fecha)
    if update_fields and set(update_fields) <= {'estado', 'fecha_actualizacion'}:
        return

    if (
        instance.fecha_vencimiento
        and instance.estado in ('activo', 'parcial')
        and timezone.localdate() > instance.fecha_vencimiento
    ):
        Prestamo.objects.filter(pk=instance.pk).update(
            estado='vencido',
            fecha_actualizacion=timezone.now(),
        )