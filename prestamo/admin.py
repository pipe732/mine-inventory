# prestamo/admin.py
from django.contrib import admin
from .models import Prestamo, ItemPrestamo


class ItemPrestamoInline(admin.TabularInline):
    model  = ItemPrestamo
    extra  = 1
    fields = ('producto', 'cantidad', 'devuelto')


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display    = ('id', 'usuario', 'estado', 'fecha_prestamo')
    list_filter     = ('estado', 'fecha_prestamo')
    search_fields   = ('usuario', 'observaciones')
    list_editable   = ('estado',)
    ordering        = ('-fecha_prestamo',)
    readonly_fields = ('fecha_prestamo', 'fecha_actualizacion')
    inlines         = [ItemPrestamoInline]

    fieldsets = (
        ('Información del préstamo', {
            'fields': ('usuario', 'observaciones', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_prestamo', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ItemPrestamo)
class ItemPrestamoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'prestamo', 'producto', 'cantidad', 'devuelto')
    list_filter   = ('devuelto',)
    search_fields = ('prestamo__usuario', 'producto__nombre')