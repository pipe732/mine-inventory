# devoluciones/admin.py
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Devolucion


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display  = (
        'id', 'prestamo_link', 'usuario_prestamo',
        'tipo_badge', 'estado_badge',
        'resumen_items_display',
        'fecha_creacion',
    )
    list_filter   = ('estado', 'devolucion_total', 'fecha_creacion')
    search_fields = ('prestamo__usuario', 'prestamo__nombre_usuario', 'motivo')
    ordering      = ('-fecha_creacion',)
    readonly_fields = (
        'fecha_creacion', 'fecha_actualizacion',
        '_aplicada', 'resumen_items',
    )
    filter_horizontal = ('items',)
    actions = ['aprobar_devoluciones', 'rechazar_devoluciones']

    fieldsets = (
        ('Préstamo y tipo', {
            'fields': ('prestamo', 'devolucion_total', 'items'),
        }),
        ('Estado', {
            'fields': ('estado', '_aplicada', 'motivo'),
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    # ── Columnas personalizadas ──────────────────────────────────────
    @admin.display(description='Préstamo', ordering='prestamo_id')
    def prestamo_link(self, obj):
        return format_html(
            '<a href="/admin/prestamo/prestamo/{}/change/">#{}</a>',
            obj.prestamo_id, obj.prestamo_id
        )

    @admin.display(description='Usuario', ordering='prestamo__usuario')
    def usuario_prestamo(self, obj):
        nombre = obj.prestamo.nombre_usuario
        doc    = obj.prestamo.usuario
        if nombre:
            return format_html('{}<br><small style="color:#999;">{}</small>', nombre, doc)
        return doc

    @admin.display(description='Tipo')
    def tipo_badge(self, obj):
        if obj.devolucion_total:
            return format_html(
                '<span style="background:#e3f2fd;color:#0d47a1;padding:2px 8px;'
                'border-radius:12px;font-size:11px;font-weight:600;">Total</span>'
            )
        return format_html(
            '<span style="background:#fff8e1;color:#f57f17;padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:600;">Parcial</span>'
        )

    @admin.display(description='Estado', ordering='estado')
    def estado_badge(self, obj):
        colores = {
            'pendiente': ('#fff8e1', '#f57f17'),
            'aprobada':  ('#e8f5e9', '#1b5e20'),
            'rechazada': ('#fce4ec', '#880e4f'),
        }
        bg, fg = colores.get(obj.estado, ('#f5f5f5', '#333'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, obj.get_estado_display()
        )

    @admin.display(description='Ítems')
    def resumen_items_display(self, obj):
        texto = obj.resumen_items
        # Truncar si es muy largo
        if len(texto) > 60:
            texto = texto[:57] + '…'
        return texto

    # ── Acciones masivas ─────────────────────────────────────────────
    @admin.action(description='Aprobar devoluciones seleccionadas')
    def aprobar_devoluciones(self, request, queryset):
        count = 0
        for dev in queryset.filter(estado__in=['pendiente', 'rechazada']):
            dev.estado = 'aprobada'
            dev.save(update_fields=['estado', 'fecha_actualizacion'])
            count += 1
        self.message_user(request, f'{count} devolución(es) aprobada(s).')

    @admin.action(description='Rechazar devoluciones seleccionadas (revierte stock)')
    def rechazar_devoluciones(self, request, queryset):
        count = 0
        for dev in queryset.filter(estado__in=['pendiente', 'aprobada']):
            dev.estado = 'rechazada'
            dev.save(update_fields=['estado', 'fecha_actualizacion'])
            count += 1
        self.message_user(request, f'{count} devolución(es) rechazada(s) y stock revertido.')