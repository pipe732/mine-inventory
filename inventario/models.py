from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo_sku = models.CharField(
        max_length=50, unique=True, verbose_name="Código / SKU"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock / Cantidad")
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
        verbose_name="Categoría"
    )
    
    numero_serie = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Número de serie"
    )

    disponible = models.BooleanField(
        default=True, 
        verbose_name="Disponible para préstamo"
    )

    ubicacion = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name="Almacén / Estante"
    )

    UNIDAD_MEDIDA_CHOICES = [
        ('unidad', 'Unidad'),
        ('kg', 'Kilogramo'),
        ('m', 'Metro'),
        ('m2', 'Metro cuadrado'),
        ('ml', 'Mililitro'),
        ('l', 'Litro'),
        ('paquete', 'Paquete'),
        ('hora', 'Hora'),
        ('dia', 'Día'),
    ]

    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_MEDIDA_CHOICES,
        default='unidad',
        verbose_name="Unidad de medida"
    )

    costo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Costo unitario (para autocomplete)"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"[{self.codigo_sku}] {self.nombre}"
    