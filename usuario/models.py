from django.db import models


class Rol(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PP', 'Pasaporte'),
        ('TI', 'Tarjeta de Identidad'),
    ]

    numero_documento = models.CharField(max_length=20, primary_key=True)
    id_rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        db_column='id_rol',
        related_name='usuarios'
    )
    nombre_completo = models.CharField(max_length=200)
    correo          = models.EmailField(max_length=255, unique=True)
    telefono        = models.CharField(max_length=20, blank=True, default='')
    tipo_documento  = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, default='CC')

    # ─── Campo contraseña (hasheada con make_password) ───────────────────────
    password = models.CharField(max_length=255, default='')

    # Relaciones auto-referenciales
    destinado = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='destinados',
        db_column='destinado'
    )
    solicitado = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='solicita',
        db_column='solicitado'
    )

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre_completo} ({self.numero_documento})"