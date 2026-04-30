from django.contrib import admin
from .models import ReporteHistorial


@admin.register(ReporteHistorial)
class ReporteHistorialAdmin(admin.ModelAdmin):
    list_display  = ('modulo', 'formato', 'nombre_archivo', 'generado_por', 'total_registros', 'fecha_generado')
    list_filter   = ('modulo', 'formato')
    search_fields = ('nombre_archivo', 'generado_por')
    readonly_fields = ('fecha_generado',)