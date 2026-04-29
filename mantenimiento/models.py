# mantenimiento/models.py
from django.db import models, transaction
from django.core.exceptions import ValidationError
from inventario.models import Producto


# ─────────────────────────────────────────────────────────────
# CONSTANTES Y CHOICES CENTRALIZADOS
# ─────────────────────────────────────────────────────────────

CATEGORIA_TIPOESTADO_CHOICES = [
    ('danado', 'Dañado'),
    ('reparacion', 'En reparación'),
    ('obsoleto', 'Obsoleto'),
    ('calibracion', 'Calibración pendiente'),
    ('preventivo', 'Mantenimiento preventivo'),
    ('otro', 'Otro'),
]

IMPACTO_DISPONIBILIDAD_CHOICES = [
    ('no_disponible', 'No disponible'),
    ('parcialmente_disponible', 'Parcialmente disponible'),
    ('disponible_restringido', 'Disponible con restricción'),
]

TIPO_MANTENIMIENTO_CHOICES = [
    ('correctivo', 'Correctivo'),
    ('preventivo', 'Preventivo'),
    ('calibracion', 'Calibración'),
    ('reparacion_externa', 'Reparación externa'),
    ('otro', 'Otro'),
]

PRIORIDAD_MANTENIMIENTO_CHOICES = [
    ('baja', 'Baja'),
    ('media', 'Media'),
    ('alta', 'Alta'),
    ('critica', 'Crítica'),
]

ESTADO_REGISTRO_CHOICES = [
    ('abierto', 'Abierto'),
    ('en_proceso', 'En proceso'),
    ('cerrado', 'Cerrado'),
    ('cancelado', 'Cancelado'),
]

MOTIVO_CAMBIO_CHOICES = [
    ('correccion_error', 'Corrección de error'),
    ('actualizacion_imprevisto', 'Actualización por imprevisto'),
    ('adicion_evidencia', 'Adición de evidencia'),
    ('ajuste_estado', 'Ajuste de estado'),
    ('otro', 'Otro'),
]

# Constantes para disponibilidad
ESTADOS_MANTENIMIENTO_ACTIVOS = {'abierto', 'en_proceso'}
IMPACTO_NO_DISPONIBLE = 'no_disponible'

# ─────────────────────────────────────────────────────────────
# TIPOS DE ESTADO
# ─────────────────────────────────────────────────────────────

class TipoEstado(models.Model):
    """
    Define tipos de estado posibles para un producto.
    Determina impacto en disponibilidad y categorización.
    """

    nombre = models.CharField(
        max_length=120,
        unique=True,
        verbose_name="Nombre del estado"
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código abreviado"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción breve"
    )
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_TIPOESTADO_CHOICES,
        verbose_name="Categoría"
    )
    impacto_disponibilidad = models.CharField(
        max_length=40,
        choices=IMPACTO_DISPONIBILIDAD_CHOICES,
        default=IMPACTO_NO_DISPONIBLE,
        verbose_name="Impacto en disponibilidad"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name="Color asociado"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Creado por"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = "Tipo de Estado"
        verbose_name_plural = "Tipos de Estado"
        ordering = ['nombre']
        db_table = 'mantenimiento_tipoestado'
# ─────────────────────────────────────────────────────────────
# REGISTRO DE MANTENIMIENTO
# ─────────────────────────────────────────────────────────────

class Mantenimiento(models.Model):
    """
    Registro de órdenes de trabajo (OT) para mantenimiento de productos.
    Maneja correctivo, preventivo, calibración y reparaciones externas.
    """

    # ── Relaciones ────────────────────────────────────────────────
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='mantenimientos',
        verbose_name="Ítem / Herramienta"
    )
    tipo_estado = models.ForeignKey(
        TipoEstado,
        on_delete=models.PROTECT,
        related_name='mantenimientos',
        verbose_name="Tipo de estado actual"
    )
    responsable = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_responsable',
        verbose_name="Responsable / Técnico"
    )
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_creados',
        verbose_name="Registrado por"
    )
    actualizado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_actualizados',
        verbose_name="Última edición por"
    )

    # ── Campos de clasificación ───────────────────────────────────
    tipo_mantenimiento = models.CharField(
        max_length=30,
        choices=TIPO_MANTENIMIENTO_CHOICES,
        verbose_name="Tipo de mantenimiento"
    )
    estado_registro = models.CharField(
        max_length=20,
        choices=ESTADO_REGISTRO_CHOICES,
        default='abierto',
        verbose_name="Estado del registro"
    )
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_MANTENIMIENTO_CHOICES,
        default='media',
        verbose_name="Prioridad / urgencia"
    )

    # ── Fechas ────────────────────────────────────────────────────
    fecha_reporte = models.DateField(
        verbose_name="Fecha de reporte / detección"
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha inicio mantenimiento"
    )
    fecha_fin_estimada = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha estimada de entrega"
    )
    fecha_fin_real = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha entrega real"
    )

    # ── Descripción y acciones ────────────────────────────────────
    descripcion_problema = models.TextField(
        verbose_name="Descripción del problema / falla"
    )
    acciones_realizadas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Acciones realizadas / planificadas"
    )
    materiales_usados = models.TextField(
        blank=True,
        null=True,
        verbose_name="Materiales / repuestos usados (deprecado: ver ConsumoRepuesto)"
    )
    notas_adicionales = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas adicionales"
    )

    # ── Recursos y costos ─────────────────────────────────────────
    tiempo_empleado_horas = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Tiempo empleado (horas)"
    )
    costo_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Costo estimado"
    )
    costo_real = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Costo real"
    )

    # ── Evidencia y trazabilidad ──────────────────────────────────
    evidencia_adicional = models.FileField(
        upload_to='mantenimiento/evidencias/',
        blank=True,
        null=True,
        verbose_name="Evidencia adjunta"
    )
    ubicacion_snapshot = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Ubicación al momento del registro"
    )

    # ── Auditoría ─────────────────────────────────────────────────
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validaciones de integridad del modelo."""
        from django.core.exceptions import ValidationError as DjangoValidationError
        from django.utils.translation import gettext_lazy as _
        
        errors = {}

        if self.fecha_fin_estimada and self.fecha_inicio and self.fecha_fin_estimada < self.fecha_inicio:
            errors['fecha_fin_estimada'] = _('La fecha estimada debe ser posterior a la de inicio.')

        if self.fecha_fin_real and self.fecha_fin_estimada and self.fecha_fin_real > self.fecha_fin_estimada:
            # Nota: Permitimos retrasos, solo advertencia en logs
            pass

        if self.tiempo_empleado_horas and self.tiempo_empleado_horas < 0:
            errors['tiempo_empleado_horas'] = _('El tiempo no puede ser negativo.')

        if self.costo_estimado and self.costo_estimado < 0:
            errors['costo_estimado'] = _('El costo estimado no puede ser negativo.')

        if self.costo_real and self.costo_real < 0:
            errors['costo_real'] = _('El costo real no puede ser negativo.')

        if errors:
            raise DjangoValidationError(errors)

    @staticmethod
    def _calcular_disponibilidad_producto(producto):
        """
        Calcula si un producto está disponible.
        
        Retorna False si existe al menos un mantenimiento
        activo (abierto/en_proceso) con impacto no_disponible.
        """
        return not Mantenimiento.objects.filter(
            producto=producto,
            estado_registro__in=ESTADOS_MANTENIMIENTO_ACTIVOS,
            tipo_estado__impacto_disponibilidad=IMPACTO_NO_DISPONIBLE,
        ).exists()

    def _actualizar_disponibilidad(self):
        """Actualiza el estado de disponibilidad del producto si es necesario."""
        if not self.producto_id:
            return

        disponible = self._calcular_disponibilidad_producto(self.producto)
        if self.producto.disponible != disponible:
            self.producto.disponible = disponible
            self.producto.save(update_fields=['disponible', 'actualizado_en'])

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Al guardar:
        1. Snapshot de ubicación (si es nuevo)
        2. Validaciones
        3. Actualiza disponibilidad del producto
        """
        # Snapshot de ubicación en la creación
        if not self.pk and self.producto_id and self.producto.ubicacion:
            self.ubicacion_snapshot = self.producto.ubicacion

        self.clean()
        super().save(*args, **kwargs)
        self._actualizar_disponibilidad()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """Al eliminar, recalcula disponibilidad del producto."""
        producto = self.producto if self.producto_id else None
        super().delete(*args, **kwargs)
        
        if producto:
            disponible = self._calcular_disponibilidad_producto(producto)
            if producto.disponible != disponible:
                producto.disponible = disponible
                producto.save(update_fields=['disponible', 'actualizado_en'])

    def registrar_cambio(self, *, editado_por, motivo_edicion, cambios, detalle_motivo=''):
        """Registra un cambio en la auditoría del mantenimiento."""
        if not cambios:
            return None
        return MantenimientoCambio.objects.create(
            mantenimiento=self,
            editado_por=editado_por,
            motivo_edicion=motivo_edicion,
            detalle_motivo=detalle_motivo,
            cambios=cambios,
        )

    def __str__(self):
        return f"[{self.tipo_mantenimiento}] {self.producto} — {self.fecha_reporte}"

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['-fecha_reporte']
        indexes = [
            models.Index(fields=['estado_registro', '-fecha_reporte']),
            models.Index(fields=['producto', '-fecha_reporte']),
            models.Index(fields=['responsable', '-fecha_reporte']),
        ]


# ─────────────────────────────────────────────────────────────
# AUDITORÍA DE CAMBIOS
# ─────────────────────────────────────────────────────────────

class MantenimientoCambio(models.Model):
    """
    Registro de auditoría para cambios en órdenes de trabajo.
    Mantiene un historial inmutable de quién cambió qué y cuándo.
    """

    mantenimiento = models.ForeignKey(
        Mantenimiento,
        on_delete=models.CASCADE,
        related_name='cambios_auditoria',
        verbose_name='Mantenimiento'
    )
    editado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cambios_mantenimiento',
        verbose_name='Editado por'
    )
    fecha_edicion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de edición'
    )
    motivo_edicion = models.CharField(
        max_length=40,
        choices=MOTIVO_CAMBIO_CHOICES,
        verbose_name='Motivo de edición'
    )
    detalle_motivo = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Detalle del motivo'
    )
    cambios = models.JSONField(
        default=dict,
        verbose_name='Campos modificados'
    )

    def __str__(self):
        return f"Cambio OT #{self.mantenimiento_id} - {self.fecha_edicion:%Y-%m-%d %H:%M}"

    class Meta:
        verbose_name = 'Cambio de mantenimiento'
        verbose_name_plural = 'Cambios de mantenimiento'
        ordering = ['-fecha_edicion']
        indexes = [
            models.Index(fields=['mantenimiento', '-fecha_edicion']),
        ]


# ─────────────────────────────────────────────────────────────
# CONSUMO DE REPUESTOS EN MANTENIMIENTO
# ─────────────────────────────────────────────────────────────

class ConsumoRepuesto(models.Model):
    """
    Registra cada repuesto consumido en una orden de trabajo (mantenimiento).
    Actualiza automáticamente el stock y permite rastrear costos y trazabilidad.
    
    Nota: El stock se ajusta en tiempo real; considera usar transacciones para
    operaciones en lote en vistas.
    """

    mantenimiento = models.ForeignKey(
        Mantenimiento,
        on_delete=models.CASCADE,
        related_name='repuestos_consumidos',
        verbose_name="Orden de Trabajo"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='consumos_mantenimiento',
        verbose_name="Repuesto"
    )

    # ── Cantidad y medida ─────────────────────────────────
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Cantidad utilizada"
    )

    # ── Costos ────────────────────────────────────────────
    costo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Costo unitario (en el momento)"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        verbose_name="Subtotal (cantidad × costo unitario)"
    )

    # ── Trazabilidad ──────────────────────────────────────
    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Lote / Número de serie"
    )

    almacen_origen = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Almacén / Ubicación de origen"
    )

    # ── Auditoría ─────────────────────────────────────────
    consumido_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repuestos_consumidos',
        verbose_name="Consumido por (técnico)"
    )

    fecha_consumo = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora de consumo"
    )

    # ── Devoluciones ──────────────────────────────────────
    devuelto = models.BooleanField(
        default=False,
        verbose_name="¿Fue devuelto?"
    )

    cantidad_devuelta = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Cantidad devuelta"
    )

    fecha_devolucion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de devolución"
    )

    def clean(self):
        """Validaciones de integridad."""
        from django.core.exceptions import ValidationError as DjangoValidationError
        from django.utils.translation import gettext_lazy as _
        
        errors = {}

        if self.cantidad <= 0:
            errors['cantidad'] = _('La cantidad debe ser mayor a 0.')

        if self.costo_unitario < 0:
            errors['costo_unitario'] = _('El costo unitario no puede ser negativo.')

        if self.devuelto and (not self.cantidad_devuelta or self.cantidad_devuelta <= 0):
            errors['cantidad_devuelta'] = _('Debe especificar cantidad devuelta mayor a 0.')

        if self.devuelto and self.cantidad_devuelta and self.cantidad_devuelta > self.cantidad:
            errors['cantidad_devuelta'] = _('No puede devolver más de lo consumido.')

        if errors:
            raise DjangoValidationError(errors)

    def _movimiento_neto(self):
        """
        Calcula el movimiento neto de stock (positivo o negativo).
        Mantiene precisión con Decimal.
        """
        if self.devuelto:
            return self.cantidad_devuelta or 0
        return -self.cantidad

    @staticmethod
    def _ajustar_stock_producto(producto, delta):
        """
        Ajusta el stock de un producto de forma atómica.
        
        Delta positivo = suma; Delta negativo = resta
        """
        if not delta or delta == 0:
            return
        
        producto.stock = producto.stock + delta
        producto.save(update_fields=['stock', 'actualizado_en'])

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Al guardar:
        1. Calcula automáticamente el subtotal
        2. Guarda la ubicación actual del producto (si es nuevo)
        3. Actualiza el stock del inventario de forma atómica
        """
        self.clean()
        
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.costo_unitario

        # Si es nuevo, guardar ubicación actual del producto
        if not self.pk and self.producto.ubicacion:
            self.almacen_origen = self.producto.ubicacion

        # Obtener estado anterior si es edición
        stock_anterior = 0
        producto_anterior = None
        
        if self.pk:
            try:
                anterior = ConsumoRepuesto.objects.select_related('producto').get(pk=self.pk)
                stock_anterior = anterior._movimiento_neto()
                producto_anterior = anterior.producto
            except ConsumoRepuesto.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        stock_nuevo = self._movimiento_neto()

        # Ajustar stock del producto
        if producto_anterior and producto_anterior.pk != self.producto_id:
            # Si cambió el producto: revertir anterior y aplicar nuevo
            self._ajustar_stock_producto(producto_anterior, -stock_anterior)
            self._ajustar_stock_producto(self.producto, stock_nuevo)
        else:
            # Mismo producto: aplicar diferencia
            self._ajustar_stock_producto(self.producto, stock_nuevo - stock_anterior)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """Al eliminar, revierte el movimiento de stock."""
        producto = self.producto
        ajuste = -self._movimiento_neto()
        super().delete(*args, **kwargs)
        self._ajustar_stock_producto(producto, ajuste)

    def __str__(self):
        estado = "Devuelto" if self.devuelto else "Consumido"
        return f"{estado}: {self.producto.nombre} × {self.cantidad} en OT #{self.mantenimiento_id}"

    class Meta:
        verbose_name = "Consumo de Repuesto"
        verbose_name_plural = "Consumos de Repuestos"
        ordering = ['-fecha_consumo']
        indexes = [
            models.Index(fields=['mantenimiento', '-fecha_consumo']),
            models.Index(fields=['producto', '-fecha_consumo']),
            models.Index(fields=['devuelto', '-fecha_consumo']),
        ]