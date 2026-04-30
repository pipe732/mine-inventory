# devoluciones/admin.py
from django.contrib import admin
from .models import Devolucion


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display    = ('id', 'prestamo', 'devolucion_total', 'estado', 'fecha_creacion')
    list_filter     = ('estado', 'devolucion_total', 'fecha_creacion')
    search_fields   = ('prestamo__usuario', 'motivo')
    list_editable   = ('estado',)
    ordering        = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ('Información del préstamo', {
            'fields': ('prestamo', 'items', 'devolucion_total')
        }),
        ('Devolución', {
            'fields': ('motivo', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )