# prestamos/models.py
from django.db import models


class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo',     'Activo'),
        ('devuelto',   'Devuelto'),
        ('vencido',    'Vencido'),
    ]

    usuario             = models.CharField(max_length=150)
    producto            = models.CharField(max_length=255)
    cantidad            = models.PositiveIntegerField()
    observaciones       = models.TextField(blank=True)
    estado              = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_prestamo      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Préstamo #{self.id} — {self.usuario} / {self.producto}"

    class Meta:
        verbose_name        = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering            = ['-fecha_prestamo']