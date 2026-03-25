# prestamos/admin.py
from django.contrib import admin
from .models import Prestamo


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display    = ('id', 'usuario', 'producto', 'cantidad', 'estado', 'fecha_prestamo')
    list_filter     = ('estado', 'fecha_prestamo')
    search_fields   = ('usuario', 'producto', 'observaciones')
    list_editable   = ('estado',)
    ordering        = ('-fecha_prestamo',)
    readonly_fields = ('fecha_prestamo', 'fecha_actualizacion')

    fieldsets = (
        ('Información del préstamo', {
            'fields': ('usuario', 'producto', 'cantidad')
        }),
        ('Detalles', {
            'fields': ('observaciones', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_prestamo', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )