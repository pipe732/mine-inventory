from django.db import models


class Almacen(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # ← unique
    detalles = models.TextField(blank=True, null=True)
    capacidad = models.PositiveIntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Estante(models.Model):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50, unique=True)  # ← unique
    detalles = models.TextField(blank=True, null=True)
    capacidad = models.PositiveIntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo