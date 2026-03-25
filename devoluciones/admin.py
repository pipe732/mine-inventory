# devoluciones/admin.py
from django.contrib import admin
from .models import Devolucion


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display   = ('id', 'numero_orden', 'producto', 'cantidad', 'estado', 'fecha_creacion')
    list_filter    = ('estado', 'fecha_creacion')
    search_fields  = ('numero_orden', 'producto', 'motivo')
    list_editable  = ('estado',)
    ordering       = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ('Información del pedido', {
            'fields': ('numero_orden', 'producto', 'cantidad')
        }),
        ('Devolución', {
            'fields': ('motivo', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )