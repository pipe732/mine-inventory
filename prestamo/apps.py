# prestamo/apps.py
from django.apps import AppConfig


class PrestamoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prestamo'

    def ready(self):
        import prestamo.signals  # noqa: F401  — conecta los signals