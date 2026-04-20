# devoluciones/apps.py
from django.apps import AppConfig


class DevolucionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'devoluciones'

    def ready(self):
        import devoluciones.signals  # noqa: F401  — conecta los signals