# prestamo/admin.py
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Prestamo, ItemPrestamo


class ItemPrestamoInline(admin.TabularInline):
    model       = ItemPrestamo
    extra       = 0          # sin filas vacías por defecto
    min_num     = 1
    fields      = ('producto', 'cantidad', 'devuelto')
    raw_id_fields = ('producto',)
    show_change_link = True


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'usuario', 'nombre_usuario',
        'estado_badge', 'urgencia_badge',
        'fecha_prestamo', 'fecha_vencimiento',
    )
    list_filter  = ('estado', 'fecha_prestamo', 'fecha_vencimiento')
    search_fields = ('usuario', 'nombre_usuario', 'observaciones')
    ordering      = ('-fecha_prestamo',)
    readonly_fields = ('fecha_prestamo', 'fecha_actualizacion')
    inlines       = [ItemPrestamoInline]
    actions       = ['marcar_vencidos', 'cancelar_prestamos']

    fieldsets = (
        ('Responsable', {
            'fields': ('usuario', 'nombre_usuario'),
        }),
        ('Estado y fechas', {
            'fields': ('estado', 'fecha_vencimiento', 'fecha_prestamo', 'fecha_actualizacion'),
        }),
        ('Notas', {
            'fields': ('observaciones',),
            'classes': ('collapse',),
        }),
    )

    # ── Columnas con color ───────────────────────────────────────────
    @admin.display(description='Estado', ordering='estado')
    def estado_badge(self, obj):
        colores = {
            'activo':   ('#e8f5e9', '#1b5e20'),
            'parcial':  ('#fff8e1', '#f57f17'),
            'devuelto': ('#e3f2fd', '#0d47a1'),
            'vencido':  ('#fce4ec', '#880e4f'),
        }
        bg, fg = colores.get(obj.estado, ('#f5f5f5', '#333'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, obj.get_estado_display()
        )

    @admin.display(description='Urgencia')
    def urgencia_badge(self, obj):
        mapa = {
            'sin_fecha': ('—',         '#999',    'transparent'),
            'ok':        ('OK',        '#2e7d32', '#e8f5e9'),
            'proximo':   ('⚠ Próximo', '#e65100', '#fff3e0'),
            'vencido':   ('✗ Vencido', '#b71c1c', '#fce4ec'),
        }
        label, fg, bg = mapa.get(obj.urgencia, ('—', '#999', 'transparent'))
        dias = obj.dias_restantes
        sufijo = ''
        if dias is not None:
            if dias == 0:
                sufijo = ' (hoy)'
            elif dias > 0:
                sufijo = f' ({dias}d)'
            else:
                sufijo = f' ({abs(dias)}d atrás)'
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}{}</span>',
            bg, fg, label, sufijo
        )

    # ── Acciones masivas ─────────────────────────────────────────────
    @admin.action(description='Marcar como vencidos los préstamos con fecha pasada')
    def marcar_vencidos(self, request, queryset):
        hoy     = timezone.localdate()
        updated = queryset.filter(
            estado__in=['activo', 'parcial'],
            fecha_vencimiento__lt=hoy,
        ).update(estado='vencido', fecha_actualizacion=timezone.now())
        self.message_user(request, f'{updated} préstamo(s) marcados como vencidos.')

    @admin.action(description='Cancelar préstamos seleccionados (devuelve stock)')
    def cancelar_prestamos(self, request, queryset):
        count = 0
        for prestamo in queryset.exclude(estado='devuelto'):
            prestamo.cancelar()
            count += 1
        self.message_user(request, f'{count} préstamo(s) cancelados y stock restaurado.')


@admin.register(ItemPrestamo)
class ItemPrestamoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'prestamo', 'producto', 'cantidad', 'devuelto_badge')
    list_filter   = ('devuelto',)
    search_fields = ('prestamo__usuario', 'producto__nombre')
    raw_id_fields = ('prestamo', 'producto')

    @admin.display(description='Devuelto', boolean=True)
    def devuelto_badge(self, obj):
        return obj.devuelto