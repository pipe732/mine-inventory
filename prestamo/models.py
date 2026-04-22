# prestamo/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from inventario.models import Producto

import django


class Prestamo(models.Model):

    ESTADO_CHOICES = [
        ('activo',   'Activo'),
        ('parcial',  'Devuelto parcialmente'),
        ('devuelto', 'Devuelto'),
        ('vencido',  'Vencido'),
    ]

    usuario           = models.CharField(
        max_length=150,
        verbose_name='Documento / ID del usuario',
    )
    nombre_usuario    = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Nombre del responsable',
    )
    observaciones     = models.TextField(
        blank=True,
        verbose_name='Observaciones',
    )
    estado            = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo',
        db_index=True,
        verbose_name='Estado',
    )
    fecha_prestamo    = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de préstamo',
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización',
    )
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Fecha de vencimiento',
        help_text='Fecha límite para la devolución. Dejar vacío si no aplica.',
    )

    # ── Validaciones ────────────────────────────────────────────────────
    def clean(self):
        super().clean()
        errors = {}

        if not self.usuario or not self.usuario.strip():
            errors['usuario'] = 'El documento / ID del usuario no puede estar vacío.'

        if self.fecha_vencimiento:
            if not self.pk and self.fecha_vencimiento < timezone.localdate():
                errors['fecha_vencimiento'] = 'La fecha de vencimiento no puede ser en el pasado.'

        if errors:
            raise ValidationError(errors)

    # ── Propiedades calculadas ──────────────────────────────────────────
    @property
    def esta_vencido(self):
        if not self.fecha_vencimiento:
            return False
        if self.estado == 'devuelto':
            return False
        return timezone.localdate() > self.fecha_vencimiento

    @property
    def dias_restantes(self):
        if not self.fecha_vencimiento:
            return None
        return (self.fecha_vencimiento - timezone.localdate()).days

    @property
    def urgencia(self):
        dias = self.dias_restantes
        if dias is None:
            return 'sin_fecha'
        if dias < 0:
            return 'vencido'
        if dias <= 3:
            return 'proximo'
        return 'ok'

    @property
    def tiene_items_pendientes(self):
        return self.items.filter(devuelto=False).exists()

    # ── Lógica de negocio ───────────────────────────────────────────────
    def actualizar_estado(self):
        items = self.items.all()
        if not items.exists():
            return

        total     = items.count()
        devueltos = items.filter(devuelto=True).count()

        if devueltos == total:
            nuevo = 'devuelto'
        elif devueltos == 0:
            nuevo = 'vencido' if self.esta_vencido else 'activo'
        else:
            nuevo = 'parcial'

        if self.estado != nuevo:
            self.estado = nuevo
            self.save(update_fields=['estado', 'fecha_actualizacion'])

    def cancelar(self):
        for item in self.items.filter(devuelto=False).select_related('producto'):
            item.producto.stock += item.cantidad
            item.producto.save(update_fields=['stock', 'actualizado_en'])
            item.devuelto = True
            item.save(update_fields=['devuelto'])
        self.estado = 'devuelto'
        self.save(update_fields=['estado', 'fecha_actualizacion'])

    def __str__(self):
        nombre = f' ({self.nombre_usuario})' if self.nombre_usuario else ''
        return f'Préstamo #{self.pk} — {self.usuario}{nombre}'

    class Meta:
        verbose_name        = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering            = ['-fecha_prestamo']


class ItemPrestamo(models.Model):

    prestamo = models.ForeignKey(
        Prestamo,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Préstamo',
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='items_prestamo',
        verbose_name='Producto',
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad prestada',
    )
    devuelto = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Devuelto',
    )

    # ── Validaciones ────────────────────────────────────────────────────
    def clean(self):
        super().clean()
        if self.cantidad < 1:
            raise ValidationError({'cantidad': 'La cantidad debe ser al menos 1.'})

    # ── Propiedades ─────────────────────────────────────────────────────
    @property
    def cantidad_pendiente(self):
        return 0 if self.devuelto else self.cantidad

    def __str__(self):
        estado = '✓' if self.devuelto else '✗'
        return f'{estado} {self.producto.nombre} ×{self.cantidad} [{self.prestamo}]'

    class Meta:
        verbose_name        = 'Ítem de préstamo'
        verbose_name_plural = 'Ítems de préstamo'
        constraints = [
            # Compatible con Django 4.x (check=) y 5.1+ (condition=)
            models.CheckConstraint(
                **({'condition' if django.VERSION >= (5, 1) else 'check': models.Q(cantidad__gte=1)}),
                name='itemprestamo_cantidad_gte_1',
            )
        ]