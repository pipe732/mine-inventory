from django.db import models

class EstadoHerramienta(models.Model): #creacion de la clase
    
    #Nombre de la herramienta (pendiente para foreign key con modulo herramienta) 
    nombre_herramienta = models.CharField(max_length=150, verbose_name="Nombre de la herramienta")
    
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    
    #4 Descripción 
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    
    #5 Categoría (Opciones desplegables)
    OPCIONES_CATEGORIA = [
        ('disponible', 'Disponible'),
        ('en_reparacion', 'En reparación'),
        ('danada', 'Dañada'),
    ]
    categoria = models.CharField(max_length=20, choices=OPCIONES_CATEGORIA, verbose_name="Categoría")
    #opciones de estado
    OPCIONES_ESTADO = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=15, choices=OPCIONES_ESTADO, default='activo', verbose_name="Estado")

    def __str__(self):
        return f"[{self.codigo}] {self.nombre_herramienta} - {self.get_categoria_display()}"

    class Meta:
        verbose_name = "Estado de Herramienta"
        verbose_name_plural = "Estados de Herramientas"
        
# === NUEVO CATÁLOGO DE TIPOS DE ESTADO (separado) ===
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
        max_length=7,  # #RRGGBB
        blank=True,
        verbose_name="Color asociado"
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Creado por"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tipo de Estado (Catálogo)"
        verbose_name_plural = "Tipos de Estado (Catálogo)"
        ordering = ['nombre']
        db_table = 'mantenimiento_tipoestado'   # ← nombre explícito en BD para evitar conflictos

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"