from django.db import models


class ReporteHistorial(models.Model):
    MODULO_CHOICES = [
        ('inventario',    'Inventario'),
        ('prestamos',     'Préstamos'),
        ('devoluciones',  'Devoluciones'),
        ('mantenimiento', 'Mantenimiento'),
        ('almacenamiento','Almacenamiento'),
        ('usuarios',      'Usuarios'),
    ]
    FORMATO_CHOICES = [
        ('pdf',   'PDF'),
        ('excel', 'Excel'),
    ]

    modulo        = models.CharField(max_length=30, choices=MODULO_CHOICES, verbose_name='Módulo')
    formato       = models.CharField(max_length=10, choices=FORMATO_CHOICES, verbose_name='Formato')
    nombre_archivo = models.CharField(max_length=255, verbose_name='Nombre de archivo')
    generado_por  = models.CharField(max_length=150, default='Sistema', verbose_name='Generado por')
    fecha_generado = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de generación')
    total_registros = models.PositiveIntegerField(default=0, verbose_name='Total de registros')

    def __str__(self):
        return f'{self.get_modulo_display()} — {self.formato.upper()} — {self.fecha_generado:%d/%m/%Y %H:%M}'

    class Meta:
        verbose_name        = 'Historial de Reporte'
        verbose_name_plural = 'Historial de Reportes'
        ordering            = ['-fecha_generado']