from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Rol, Usuario


# ─────────────────────────────────────────────────────────────
#  Señal: crea los roles base al ejecutar migrate
# ─────────────────────────────────────────────────────────────
@receiver(post_migrate)
def crear_roles_base(sender, **kwargs):
    """
    Se ejecuta automáticamente después de cada `manage.py migrate`.
    Garantiza que los roles Admin (id=1) y Usuario (id=2) existan.
    """
    if sender.name == 'usuario':          # solo reacciona a la app 'usuario'
        Rol.objects.get_or_create(id=1, defaults={'nombre': 'Admin'})
        Rol.objects.get_or_create(id=2, defaults={'nombre': 'Usuario'})


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
    list_display    = ('numero_documento', 'nombre_completo', 'correo',
                       'tipo_documento', 'id_rol', 'telefono')
    list_filter     = ('id_rol', 'tipo_documento')
    search_fields   = ('numero_documento', 'nombre_completo', 'correo')
    ordering        = ('nombre_completo',)
    readonly_fields = ('numero_documento',)

    fieldsets = (
        ('Información personal', {
            'fields': ('numero_documento', 'nombre_completo', 'tipo_documento',
                       'correo', 'telefono'),
        }),
        ('Acceso', {
            'fields': ('id_rol', 'password'),
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