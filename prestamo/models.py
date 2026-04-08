# prestamos/models.py
from django.db import models
from inventario.models import Producto


class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo',   'Activo'),
        ('devuelto', 'Devuelto'),
        ('parcial',  'Devuelto parcialmente'),
        ('vencido',  'Vencido'),
    ]

    usuario             = models.CharField(max_length=150)
    observaciones       = models.TextField(blank=True)
    estado              = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_prestamo      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Préstamo #{self.id} — {self.usuario}"

    def actualizar_estado(self):
        """Recalcula el estado según los ítems devueltos."""
        items = self.items.all()
        if not items.exists():
            return
        devueltos = items.filter(devuelto=True).count()
        total     = items.count()
        if devueltos == 0:
            self.estado = 'activo'
        elif devueltos == total:
            self.estado = 'devuelto'
        else:
            self.estado = 'parcial'
        self.save(update_fields=['estado', 'fecha_actualizacion'])

    class Meta:
        verbose_name        = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering            = ['-fecha_prestamo']


class ItemPrestamo(models.Model):
    """Una herramienta/producto del inventario dentro de un préstamo."""

    prestamo  = models.ForeignKey(
                    Prestamo,
                    on_delete=models.CASCADE,
                    related_name='items'
                )
    producto  = models.ForeignKey(
                    Producto,
                    on_delete=models.PROTECT,
                    related_name='items_prestamo',
                    verbose_name='Producto'
                )
    cantidad  = models.PositiveIntegerField(default=1)
    devuelto  = models.BooleanField(default=False)

    def __str__(self):
        estado = "✓" if self.devuelto else "✗"
        return f"{estado} {self.producto.nombre} ×{self.cantidad} [{self.prestamo}]"

    class Meta:
        verbose_name        = 'Ítem de préstamo'
        verbose_name_plural = 'Ítems de préstamo'