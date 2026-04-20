# devoluciones/models.py
from django.db import models
from django.core.exceptions import ValidationError
from prestamo.models import Prestamo, ItemPrestamo


class Devolucion(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada',  'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    prestamo = models.ForeignKey(
        Prestamo,
        on_delete=models.PROTECT,
        related_name='devoluciones',
        verbose_name='Préstamo',
    )
    items = models.ManyToManyField(
        ItemPrestamo,
        related_name='devoluciones',
        blank=True,
        verbose_name='Ítems devueltos',
    )
    devolucion_total = models.BooleanField(
        default=True,
        verbose_name='Devolución total',
        help_text='True = todas las herramientas; False = devolución parcial.',
    )
    motivo = models.TextField(
        blank=True,
        default='',
        verbose_name='Motivo',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        db_index=True,
        verbose_name='Estado',
    )
    # Bandera interna: indica si aplicar() ya fue ejecutado
    # (evita doble descuento/restauración de stock)
    _aplicada = models.BooleanField(
        default=False,
        editable=False,
        verbose_name='Stock ya aplicado',
        help_text='Uso interno. True = el stock ya fue modificado por esta devolución.',
        db_column='aplicada',
    )
    fecha_creacion      = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True,     verbose_name='Última actualización')

    # ── Validaciones a nivel de modelo ─────────────────────────────────
    def clean(self):
        super().clean()
        errors = {}

        # El motivo es obligatorio en devoluciones parciales
        # (solo podemos validarlo si ya tenemos pk, porque items es M2M)
        if not self.devolucion_total and not (self.motivo or '').strip():
            errors['motivo'] = 'El motivo es obligatorio en devoluciones parciales.'

        if errors:
            raise ValidationError(errors)

    # ── Lógica de negocio ───────────────────────────────────────────────
    def aplicar(self):
        """
        Marca los ítems seleccionados como devueltos y restaura el stock.
        Idempotente: si ya fue aplicada, no hace nada.
        """
        if self._aplicada:
            return

        for item in self.items.select_related('producto'):
            if not item.devuelto:
                item.devuelto = True
                item.save(update_fields=['devuelto'])
            item.producto.stock += item.cantidad
            item.producto.save(update_fields=['stock', 'actualizado_en'])

        self._aplicada = True
        self.save(update_fields=['_aplicada', 'fecha_actualizacion'])

        # Recalcular estado del préstamo
        self.prestamo.actualizar_estado()

    def revertir(self):
        """
        Revierte los efectos de aplicar(): descuenta el stock de vuelta
        y desmarca los ítems como devueltos.
        Solo tiene efecto si la devolución fue previamente aplicada.
        """
        if not self._aplicada:
            return

        for item in self.items.select_related('producto'):
            item.producto.stock = max(0, item.producto.stock - item.cantidad)
            item.producto.save(update_fields=['stock', 'actualizado_en'])
            item.devuelto = False
            item.save(update_fields=['devuelto'])

        self._aplicada = False
        self.save(update_fields=['_aplicada', 'fecha_actualizacion'])

        # Recalcular estado del préstamo
        self.prestamo.actualizar_estado()

    @property
    def es_editable(self):
        """Una devolución solo es editable mientras está pendiente."""
        return self.estado == 'pendiente'

    @property
    def resumen_items(self):
        """Texto corto con los ítems devueltos, útil para el admin y emails."""
        partes = [
            f'{item.producto.nombre} ×{item.cantidad}'
            for item in self.items.select_related('producto')
        ]
        return ', '.join(partes) if partes else '—'

    def __str__(self):
        tipo = 'total' if self.devolucion_total else 'parcial'
        return f'Devolución #{self.pk} ({tipo}) — Préstamo #{self.prestamo_id}'

    class Meta:
        verbose_name        = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering            = ['-fecha_creacion']