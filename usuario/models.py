import re
from django.db import models
from django.core.exceptions import ValidationError


# ── Validador de número de documento ─────────────────────────────────────────
def validar_numero_documento(value, tipo):
    """
    Aplica las reglas de formato según el tipo de documento.
    Lanza ValidationError si el valor no cumple.

    Reglas:
      CC  – Solo dígitos, 6 a 10 caracteres
      CE  – Letras y dígitos, 6 a 12 caracteres
      PP  – Letras y dígitos, 5 a  9 caracteres
      TI  – Solo dígitos, 10 a 11 caracteres
    """
    REGLAS = {
        'CC': (r'^\d{6,10}$',          'La Cédula de Ciudadanía debe tener entre 6 y 10 dígitos.'),
        'CE': (r'^[A-Za-z0-9]{6,12}$', 'La Cédula de Extranjería debe tener entre 6 y 12 caracteres alfanuméricos.'),
        'PP': (r'^[A-Za-z0-9]{5,9}$',  'El Pasaporte debe tener entre 5 y 9 caracteres alfanuméricos.'),
        'TI': (r'^\d{10,11}$',         'La Tarjeta de Identidad debe tener 10 u 11 dígitos.'),
    }
    patron, mensaje = REGLAS.get(tipo, (None, None))
    if patron and not re.match(patron, value):
        raise ValidationError(mensaje)


class Usuario(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PP', 'Pasaporte'),
        ('TI', 'Tarjeta de Identidad'),
    ]

    ROL_CHOICES = [
        ('Usuario', 'Usuario'),
        ('Administrador', 'Administrador'),
    ]

    numero_documento = models.CharField(max_length=20, primary_key=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Usuario')
    nombre_completo = models.CharField(max_length=200)
    correo          = models.EmailField(max_length=255, unique=True)
    telefono        = models.CharField(max_length=20, blank=True, default='')
    tipo_documento  = models.CharField(
        max_length=2,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='CC',
        verbose_name='Tipo de documento',
    )

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

    def clean(self):
        """Validación a nivel de modelo (usada por el admin y los formularios)."""
        super().clean()
        validar_numero_documento(self.numero_documento, self.tipo_documento)

    def __str__(self):
        return f"{self.nombre_completo} ({self.get_tipo_documento_display()} {self.numero_documento})"