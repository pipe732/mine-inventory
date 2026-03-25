from django.contrib import admin
from .models import TipoEstado, EstadoHerramienta


@admin.register(TipoEstado)
class TipoEstadoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'impacto_disponibilidad', 'activo', 'creado_en']
    list_filter = ['categoria', 'impacto_disponibilidad', 'activo']
    search_fields = ['nombre', 'codigo']
    readonly_fields = ['creado_en']


@admin.register(EstadoHerramienta)
class EstadoHerramientaAdmin(admin.ModelAdmin):
    list_display = ['nombre_herramienta', 'codigo', 'categoria', 'estado']
    list_filter = ['categoria', 'estado']
    search_fields = ['nombre_herramienta', 'codigo']