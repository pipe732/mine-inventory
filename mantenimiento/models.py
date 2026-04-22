# mantenimiento/models.py
from django.db import models
from inventario.models import Producto  # ← import al tope, no en la mitad


#catalogo tiposo de estado

class TipoEstado(models.Model):

    CATEGORIA_CHOICES = [
        ('danado',      'Dañado'),
        ('reparacion',  'En reparación'),
        ('obsoleto',    'Obsoleto'),
        ('calibracion', 'Calibración pendiente'),
        ('preventivo',  'Mantenimiento preventivo'),
        ('otro',        'Otro'),
    ]

    IMPACTO_CHOICES = [
        ('no_disponible',           'No disponible'),
        ('parcialmente_disponible', 'Parcialmente disponible'),
        ('disponible_restringido',  'Disponible con restricción'),
    ]

    nombre     = models.CharField(max_length=120, unique=True, verbose_name="Nombre del estado")
    codigo     = models.CharField(max_length=20,  unique=True, verbose_name="Código abreviado")
    descripcion= models.TextField(blank=True, null=True, verbose_name="Descripción breve")
    categoria  = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, verbose_name="Categoría")
    impacto_disponibilidad = models.CharField(
        max_length=40,
        choices=IMPACTO_CHOICES,
        default='no_disponible',
        verbose_name="Impacto en disponibilidad"
    )
    color      = models.CharField(max_length=7, blank=True, verbose_name="Color asociado")
    activo     = models.BooleanField(default=True, verbose_name="Activo")
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Creado por"
    )
    creado_en  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name         = "Tipo de Estado"
        verbose_name_plural  = "Tipos de Estado"
        ordering             = ['nombre']
        db_table             = 'mantenimiento_tipoestado'

#registro de mantenimiento
class Mantenimiento(models.Model):

    TIPO_CHOICES = [
        ('correctivo',         'Correctivo'),
        ('preventivo',         'Preventivo'),
        ('calibracion',        'Calibración'),
        ('reparacion_externa', 'Reparación externa'),
        ('otro',               'Otro'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    ESTADO_REGISTRO_CHOICES = [
        ('abierto',    'Abierto'),
        ('en_proceso', 'En proceso'),
        ('cerrado',    'Cerrado'),
        ('cancelado',  'Cancelado'),
    ]

    #Relaciones
    producto    = models.ForeignKey(
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
    creado_por  = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_creados',
        verbose_name="Registrado por"
    )

    #Campos
    tipo_mantenimiento  = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de mantenimiento")
    estado_registro     = models.CharField(max_length=20, choices=ESTADO_REGISTRO_CHOICES, default='abierto', verbose_name="Estado del registro")
    prioridad           = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media', verbose_name="Prioridad / urgencia")
    fecha_reporte       = models.DateField(verbose_name="Fecha de reporte / detección")
    fecha_inicio        = models.DateField(verbose_name="Fecha inicio mantenimiento")
    fecha_fin_estimada  = models.DateField(blank=True, null=True, verbose_name="Fecha estimada de entrega")
    fecha_fin_real      = models.DateField(blank=True, null=True, verbose_name="Fecha entrega real")
    tiempo_empleado_horas = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name="Tiempo empleado (horas)")
    descripcion_problema= models.TextField(verbose_name="Descripción del problema / falla")
    acciones_realizadas = models.TextField(blank=True, null=True, verbose_name="Acciones realizadas / planificadas")
    materiales_usados   = models.TextField(blank=True, null=True, verbose_name="Materiales / repuestos usados")
    notas_adicionales   = models.TextField(blank=True, null=True, verbose_name="Notas adicionales")
    evidencia_adicional = models.FileField(upload_to='mantenimiento/evidencias/', blank=True, null=True, verbose_name="Evidencia adjunta")
    ubicacion_snapshot  = models.CharField(max_length=150, blank=True, null=True, verbose_name="Ubicación al momento del registro")
    costo_estimado      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Costo estimado")
    costo_real          = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Costo real")
    actualizado_por     = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_actualizados',
        verbose_name="Última edición por"
    )
    creado_en           = models.DateTimeField(auto_now_add=True)
    actualizado_en      = models.DateTimeField(auto_now=True)

    @staticmethod
    def _calcular_disponibilidad_producto(producto):
        """
        Un producto queda no disponible si existe al menos un mantenimiento
        activo (abierto/en_proceso) con impacto no_disponible.
        """
        bloqueo = Mantenimiento.objects.filter(
            producto=producto,
            estado_registro__in=('abierto', 'en_proceso'),
            tipo_estado__impacto_disponibilidad='no_disponible',
        ).exists()
        return not bloqueo

    def _actualizar_disponibilidad(self):
        if not self.producto_id:
            return

        disponible = self._calcular_disponibilidad_producto(self.producto)
        if self.producto.disponible != disponible:
            self.producto.disponible = disponible
            self.producto.save(update_fields=['disponible'])

    def save(self, *args, **kwargs):
        # Snapshot de ubicación 
        if not self.pk and self.producto_id and self.producto.ubicacion:
            self.ubicacion_snapshot = self.producto.ubicacion

        super().save(*args, **kwargs)
        self._actualizar_disponibilidad()

    def delete(self, *args, **kwargs):
        producto = self.producto if self.producto_id else None
        super().delete(*args, **kwargs)
        if producto:
            producto.disponible = self._calcular_disponibilidad_producto(producto)
            producto.save(update_fields=['disponible'])

    def __str__(self):
        return f"[{self.tipo_mantenimiento}] {self.producto} — {self.fecha_reporte}"

    @property
    def estado_permite_edicion(self):
        return self.estado_registro not in {'cancelado', 'cerrado_definitivo'}

    def registrar_cambio(self, *, editado_por, motivo_edicion, cambios, detalle_motivo=''):
        if not cambios:
            return None
        return MantenimientoCambio.objects.create(
            mantenimiento=self,
            editado_por=editado_por,
            motivo_edicion=motivo_edicion,
            detalle_motivo=detalle_motivo,
            cambios=cambios,
        )

    class Meta:
        verbose_name        = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering            = ['-fecha_reporte']


class MantenimientoCambio(models.Model):
    MOTIVO_CHOICES = [
        ('correccion_error', 'Corrección de error'),
        ('actualizacion_imprevisto', 'Actualización por imprevisto'),
        ('adicion_evidencia', 'Adición de evidencia'),
        ('ajuste_estado', 'Ajuste de estado'),
        ('otro', 'Otro'),
    ]

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
    fecha_edicion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de edición')
    motivo_edicion = models.CharField(max_length=40, choices=MOTIVO_CHOICES, verbose_name='Motivo de edición')
    detalle_motivo = models.CharField(max_length=255, blank=True, verbose_name='Detalle del motivo')
    cambios = models.JSONField(default=dict, verbose_name='Campos modificados')

    class Meta:
        verbose_name = 'Cambio de mantenimiento'
        verbose_name_plural = 'Cambios de mantenimiento'
        ordering = ['-fecha_edicion']

    def __str__(self):
        return f"Cambio OT #{self.mantenimiento_id} - {self.fecha_edicion:%Y-%m-%d %H:%M}"