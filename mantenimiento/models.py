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