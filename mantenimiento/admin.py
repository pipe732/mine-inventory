# mantenimiento/admin.py
from django.contrib import admin
from .models import TipoEstado, Mantenimiento


@admin.register(TipoEstado)
class TipoEstadoAdmin(admin.ModelAdmin):
    list_display    = ['codigo', 'nombre', 'categoria', 'impacto_disponibilidad', 'activo', 'creado_en']
    list_filter     = ['categoria', 'impacto_disponibilidad', 'activo']
    search_fields   = ['nombre', 'codigo']
    readonly_fields = ['creado_en']


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display    = ['producto', 'tipo_mantenimiento', 'tipo_estado', 'estado_registro', 'fecha_reporte', 'responsable']
    list_filter     = ['tipo_mantenimiento', 'estado_registro', 'tipo_estado']
    search_fields   = ['producto__nombre', 'producto__codigo_sku', 'descripcion_problema']
    readonly_fields = ['creado_en', 'actualizado_en', 'ubicacion_snapshot']
    date_hierarchy  = 'fecha_reporte'