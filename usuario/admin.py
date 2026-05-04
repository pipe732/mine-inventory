from django.contrib import admin
from django.contrib.auth.hashers import make_password

from django.dispatch import receiver
from .models import  Usuario




# ─────────────────────────────────────────────────────────────
#  USUARIO
# ─────────────────────────────────────────────────────────────
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display    = ('numero_documento', 'nombre_completo', 'correo',
                       'tipo_documento', 'rol', 'telefono')
    list_filter     = ('rol', 'tipo_documento')
    search_fields   = ('numero_documento', 'nombre_completo', 'correo')
    ordering        = ('nombre_completo',)
    readonly_fields = ('numero_documento',)

    fieldsets = (
        ('Información personal', {
            'fields': ('numero_documento', 'nombre_completo', 'tipo_documento',
                       'correo', 'telefono'),
        }),
        ('Acceso', {
            'fields': ('rol', 'password'),
            'description': 'La contraseña se guarda cifrada automáticamente al guardar.',
        }),
        ('Relaciones', {
            'fields': ('destinado', 'solicitado'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            raw = form.cleaned_data['password']
            if not raw.startswith(('pbkdf2_', 'bcrypt', 'argon2')):
                obj.password = make_password(raw)
        super().save_model(request, obj, form, change)