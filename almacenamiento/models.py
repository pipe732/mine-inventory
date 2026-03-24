from django.db import models

class Almacen(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Estante(models.Model):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50)

    def __str__(self):
        return self.codigo