from django.db import models
#MODELS.PY  

#1) Consultar estado de herramientas
class EstadoHerramienta(models.Model):

    nombre_herramienta = models.CharField(
        max_length=150,
        verbose_name="Nombre de la herramienta"
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código"
    )
    descripcion = models.CharField(         
        max_length=255,
        verbose_name="Descripción"
    )

    OPCIONES_CATEGORIA = [
        ('disponible', 'Disponible'),
        ('en_reparacion', 'En reparación'),
        ('danada', 'Dañada'),
    ]
    categoria = models.CharField(
        max_length=20,
        choices=OPCIONES_CATEGORIA,
        verbose_name="Categoría"
    )

    OPCIONES_ESTADO = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(
        max_length=15,
        choices=OPCIONES_ESTADO,
        default='activo',
        verbose_name="Estado"
    )

    def __str__(self):
        return f"[{self.codigo}] {self.nombre_herramienta} - {self.get_categoria_display()}"

    class Meta:
        verbose_name = "Estado de Herramienta"
        verbose_name_plural = "Estados de Herramientas"
        
#2)Crear nuevo catalogo de tipo de estado
class TipoEstado(models.Model):

    nombre = models.CharField(
        max_length=120,
        unique=True,
        verbose_name="Nombre del estado *"
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código abreviado *"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción breve"
    )
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('danado', 'Dañado'),
            ('reparacion', 'En reparación'),
            ('obsoleto', 'Obsoleto'),
            ('calibracion', 'Calibración pendiente'),
            ('preventivo', 'Mantenimiento preventivo'),
            ('otro', 'Otro'),
        ],
        verbose_name="Categoría"
    )
    impacto_disponibilidad = models.CharField(
        max_length=40,
        choices=[
            ('no_disponible', 'No disponible'),
            ('parcialmente_disponible', 'Parcialmente disponible'),
            ('disponible_restringido', 'Disponible con restricción'),
        ],
        default='no_disponible',
        verbose_name="Impacto en disponibilidad *"
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
        verbose_name = "Tipo de Estado (Catálogo)"
        verbose_name_plural = "Tipos de Estado (Catálogo)"
        ordering = ['nombre']
        db_table = 'mantenimiento_tipoestado'
        
from inventario.models import Producto

class Mantenimiento(models.Model):

    TIPO_CHOICES = [
        ('correctivo',          'Correctivo'),
        ('preventivo',          'Preventivo'),
        ('calibracion',         'Calibración'),
        ('reparacion_externa',  'Reparación externa'),
        ('otro',                'Otro'),
    ]

    ESTADO_REGISTRO_CHOICES = [
        ('abierto',     'Abierto'),
        ('en_proceso',  'En proceso'),
        ('cerrado',     'Cerrado'),
        ('cancelado',   'Cancelado'),
    ]

    # relaciones 
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='mantenimientos',
        verbose_name="Ítem / Herramienta *"
    )
    tipo_estado = models.ForeignKey(
        TipoEstado,
        on_delete=models.PROTECT,
        related_name='mantenimientos',
        verbose_name="Tipo de estado actual *"
    )
    responsable = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_responsable',
        verbose_name="Responsable / Técnico *"
    )
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_creados',
        verbose_name="Registrado por"
    )

    tipo_mantenimiento = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de mantenimiento *"
    )
    estado_registro = models.CharField(
        max_length=20,
        choices=ESTADO_REGISTRO_CHOICES,
        default='abierto',
        verbose_name="Estado del registro"
    )

    fecha_reporte = models.DateField(
        verbose_name="Fecha de reporte / detección "
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha inicio mantenimiento "
    )
    fecha_fin_estimada = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha estimada de entrega"      # ← Cambiado
    )
    fecha_fin_real = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha entrega (real)"           # ← Cambiado
    )
    descripcion_problema = models.TextField(
        verbose_name="Descripción del problema / falla *"
    )
    acciones_realizadas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Acciones realizadas / planificadas"
    )

    ubicacion_snapshot = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Almacén / Estante al momento del registro"
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


    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 1. Guardar snapshot de ubicación al crear
        if not self.pk and self.producto and self.producto.ubicacion:
            self.ubicacion_snapshot = self.producto.ubicacion

        # 2. Actualizar disponibilidad del producto según el tipo de estado
        if self.tipo_estado and self.estado_registro in ['abierto', 'en_proceso']:
            if self.tipo_estado.impacto_disponibilidad == 'no_disponible':
                self.producto.disponible = False
            else:
                self.producto.disponible = True
        else:
            # Si el registro está cerrado, cancelado o no tiene tipo_estado → disponible
            self.producto.disponible = True

        # Guardar el cambio de disponibilidad
        if self.producto.pk:
            self.producto.save(update_fields=['disponible'])

        # Guardar el mantenimiento
        super().save(*args, **kwargs)
    def __str__(self):
        return f"[{self.tipo_mantenimiento}] {self.producto} — {self.fecha_reporte}"

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['-fecha_reporte']