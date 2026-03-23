from django.contrib import admin
from .models import TipoEstado

# Register your models here.
@admin.register(TipoEstado)
class TipoEstadoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'impacto_disponibilidad', 'activo', 'creado_en']
    list_filter = ['categoria', 'impacto_disponibilidad', 'activo']
    search_fields = ['nombre', 'codigo']
    readonly_fields = ['creado_en']