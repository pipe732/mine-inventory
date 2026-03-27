from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Rol, Usuario


# ─────────────────────────────────────────────────────────────
#  ROL
# ─────────────────────────────────────────────────────────────
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering      = ('id',)


# ─────────────────────────────────────────────────────────────
#  USUARIO
# ─────────────────────────────────────────────────────────────
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display   = ('numero_documento', 'nombre_completo', 'correo',
                      'tipo_documento', 'id_rol', 'telefono')
    list_filter    = ('id_rol', 'tipo_documento')
    search_fields  = ('numero_documento', 'nombre_completo', 'correo')
    ordering       = ('nombre_completo',)
    readonly_fields = ('numero_documento',)

    fieldsets = (
        ('Información personal', {
            'fields': ('numero_documento', 'nombre_completo', 'tipo_documento',
                       'correo', 'telefono')
        }),
        ('Acceso', {
            'fields': ('id_rol', 'password'),
            'description': 'La contraseña se guarda cifrada automáticamente al guardar.'
        }),
        ('Relaciones', {
            'fields': ('destinado', 'solicitado'),
            'classes': ('collapse',),
        }),
    )

    # ── Hashear la contraseña automáticamente al crear o editar ──────────────
    def save_model(self, request, obj, form, change):
        # Si el campo password fue modificado y no está ya hasheado
        if form.cleaned_data.get('password'):
            raw = form.cleaned_data['password']
            # Solo hashea si no viene ya con el prefijo de Django
            if not raw.startswith(('pbkdf2_', 'bcrypt', 'argon2')):
                obj.password = make_password(raw)
        super().save_model(request, obj, form, change)