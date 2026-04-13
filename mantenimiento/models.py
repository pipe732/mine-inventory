# mantenimiento/models.py
from django.db import models
from inventario.models import Producto  # ← import al tope, no en la mitad


# ══════════════════════════════════════════════
# CATÁLOGO DE TIPOS DE ESTADO
# ══════════════════════════════════════════════

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


# ══════════════════════════════════════════════
# REGISTRO DE MANTENIMIENTO
# ══════════════════════════════════════════════

class Mantenimiento(models.Model):

    TIPO_CHOICES = [
        ('correctivo',         'Correctivo'),
        ('preventivo',         'Preventivo'),
        ('calibracion',        'Calibración'),
        ('reparacion_externa', 'Reparación externa'),
        ('otro',               'Otro'),
    ]

    ESTADO_REGISTRO_CHOICES = [
        ('abierto',    'Abierto'),
        ('en_proceso', 'En proceso'),
        ('cerrado',    'Cerrado'),
        ('cancelado',  'Cancelado'),
    ]

    # ── Relaciones ────────────────────────────
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

    # ── Campos ───────────────────────────────
    tipo_mantenimiento  = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de mantenimiento")
    estado_registro     = models.CharField(max_length=20, choices=ESTADO_REGISTRO_CHOICES, default='abierto', verbose_name="Estado del registro")
    fecha_reporte       = models.DateField(verbose_name="Fecha de reporte / detección")
    fecha_inicio        = models.DateField(verbose_name="Fecha inicio mantenimiento")
    fecha_fin_estimada  = models.DateField(blank=True, null=True, verbose_name="Fecha estimada de entrega")
    fecha_fin_real      = models.DateField(blank=True, null=True, verbose_name="Fecha entrega real")
    descripcion_problema= models.TextField(verbose_name="Descripción del problema / falla")
    acciones_realizadas = models.TextField(blank=True, null=True, verbose_name="Acciones realizadas / planificadas")
    ubicacion_snapshot  = models.CharField(max_length=150, blank=True, null=True, verbose_name="Ubicación al momento del registro")
    costo_estimado      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Costo estimado")
    costo_real          = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Costo real")
    creado_en           = models.DateTimeField(auto_now_add=True)
    actualizado_en      = models.DateTimeField(auto_now=True)

    # ── Lógica de negocio ────────────────────
    def _actualizar_disponibilidad(self):
        """
        Centraliza la lógica de disponibilidad en un método propio.
        Regla: si el registro está abierto/en_proceso Y el tipo de estado
        impacta disponibilidad → producto no disponible. En cualquier otro
        caso → disponible.
        """
        registro_activo = self.estado_registro in ('abierto', 'en_proceso')

        if registro_activo and self.tipo_estado_id:
            no_disp = self.tipo_estado.impacto_disponibilidad == 'no_disponible'
            self.producto.disponible = not no_disp
        else:
            # Cerrado, cancelado, o sin tipo_estado → disponible
            self.producto.disponible = True

        if self.producto.pk:
            self.producto.save(update_fields=['disponible'])

    def save(self, *args, **kwargs):
        # Snapshot de ubicación solo al crear
        if not self.pk and self.producto_id and self.producto.ubicacion:
            self.ubicacion_snapshot = self.producto.ubicacion

        self._actualizar_disponibilidad()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.tipo_mantenimiento}] {self.producto} — {self.fecha_reporte}"

    class Meta:
        verbose_name        = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering            = ['-fecha_reporte']