# devoluciones/models.py
from django.db import models
from prestamo.models import Prestamo, ItemPrestamo


class Devolucion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada',  'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    prestamo         = models.ForeignKey(
                           Prestamo,
                           on_delete=models.PROTECT,
                           related_name='devoluciones',
                           verbose_name='Préstamo'
                       )
    items            = models.ManyToManyField(
                           ItemPrestamo,
                           related_name='devoluciones',
                           verbose_name='Ítems devueltos',
                           blank=True,
                       )
    devolucion_total = models.BooleanField(
                           default=True,
                           help_text='True = todas las herramientas; False = devolución parcial'
                       )
    motivo           = models.TextField()
    estado           = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        tipo = "total" if self.devolucion_total else "parcial"
        return f"Devolución #{self.id} ({tipo}) — Préstamo #{self.prestamo_id}"

    def aplicar(self):
        """
        Marca los ítems seleccionados como devueltos,
        restaura el stock en inventario y recalcula estado del préstamo.
        """
        for item in self.items.select_related('producto'):
            item.devuelto = True
            item.save(update_fields=['devuelto'])
            # Restaurar stock al inventario
            item.producto.stock += item.cantidad
            item.producto.save(update_fields=['stock', 'actualizado_en'])
        self.prestamo.actualizar_estado()

    class Meta:
        verbose_name        = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering            = ['-fecha_creacion']