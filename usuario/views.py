import re
import csv
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.exceptions import ValidationError

from usuario.decorators import admin_required, login_required

from .models import Usuario, validar_numero_documento
from common.mixins import sesion_requerida

DOC_RULES = {
    'CC': re.compile(r'^\d{6,10}$'),
    'CE': re.compile(r'^[A-Za-z0-9]{12}$'),
    'PP': re.compile(r'^[A-Za-z0-9]{9}$'),
    'TI': re.compile(r'^\d{10}$'),
}
DOC_LABELS = {
    'CC': 'Cédula de Ciudadanía',
    'CE': 'Cédula de Extranjería',
    'PP': 'Pasaporte',
    'TI': 'Tarjeta de Identidad',
}
DOC_HINTS = {
    'CC': 'La Cédula de Ciudadanía debe tener entre 10 dígitos.',
    'CE': 'La Cédula de Extranjería debe tener entre 12 caracteres alfanuméricos.',
    'PP': 'El Pasaporte debe tener entre 9 caracteres alfanuméricos.',
    'TI': 'La Tarjeta de Identidad debe tener 10 dígitos.',
}
TIPOS_VALIDOS = set(DOC_RULES.keys())

# Roles disponibles según ROL_CHOICES del modelo
ROLES = [{'id': r[0], 'nombre': r[1]} for r in Usuario.ROL_CHOICES]


def _validar_documento(tipo, numero):
    if tipo not in TIPOS_VALIDOS:
        return 'Tipo de documento no válido.'
    if not DOC_RULES[tipo].match(numero):
        return DOC_HINTS[tipo]
    return None


# ─────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────
def login_view(request):
    if request.session.get('usuario_documento'):
        return redirect('home')

    if request.method == 'POST':
        tipo_documento = request.POST.get('tipo_documento', '').strip().upper()
        documento      = request.POST.get('documento', '').strip()
        password       = request.POST.get('password', '')

        campos_requeridos = {
            'Tipo de documento': tipo_documento,
            'Número de documento': documento,
            'Contraseña': password,
        }
        faltantes = [nombre for nombre, valor in campos_requeridos.items() if not valor]
        if faltantes:
            mensaje = (
                f"Faltan completar los siguientes campos: {', '.join(faltantes)}."
                if len(faltantes) > 1
                else f"Falta completar el campo: {faltantes[0]}."
            )
            messages.error(request, mensaje)
            return render(request, 'login.html', {
                'tipo_documento': tipo_documento,
                'documento': documento,
            })

        error_doc = _validar_documento(tipo_documento, documento)
        if error_doc:
            messages.error(request, error_doc)
            return render(request, 'login.html', {
                'tipo_documento': tipo_documento,
                'documento': documento,
            })

        try:
            usuario = Usuario.objects.get(
                numero_documento=documento,
                tipo_documento=tipo_documento,
            )
        except Usuario.DoesNotExist:
            messages.error(request, 'Documento o contraseña incorrectos.')
            return render(request, 'login.html', {
                'tipo_documento': tipo_documento,
                'documento': documento,
            })

        if not check_password(password, usuario.password):
            messages.error(request, 'Documento o contraseña incorrectos.')
            return render(request, 'login.html', {
                'tipo_documento': tipo_documento,
                'documento': documento,
            })

        request.session['usuario_documento']      = usuario.numero_documento
        request.session['usuario_nombre']         = usuario.nombre_completo
        request.session['usuario_rol']            = usuario.rol
        request.session['usuario_tipo_documento'] = usuario.tipo_documento

        rol = usuario.rol.strip().lower()
        if rol in ('administrador', 'instructor'):
            return redirect('home')
        return redirect('home_usuario')

    return render(request, 'login.html')


# ─────────────────────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────────────────────
def logout_view(request):
    request.session.flush()
    return redirect(reverse('login'))


# ─────────────────────────────────────────────────────────────
#  REGISTRO
# ─────────────────────────────────────────────────────────────
def registro_view(request):
    # Todos los roles disponibles para el registro
    """
    linea comentada temporal
    roles_disponibles = Rol.objects.all()
    """
    if request.method == 'POST':
        username       = request.POST.get('username', '').strip()
        email          = request.POST.get('email', '').strip().lower()
        tipo_documento = request.POST.get('tipo_documento', '').strip().upper()
        documento      = request.POST.get('documento', '').strip()
        password1      = request.POST.get('password1', '')
        password2      = request.POST.get('password2', '')
        # El rol siempre es 'Usuario' al registrarse; no lo elige el usuario
        rol_id = 'Usuario'

        ctx = {
            **ctx_base,
            'username':       username,
            'email':          email,
            'tipo_documento': tipo_documento,
            'documento':      documento,
        }

        # Validar campos obligatorios (rol ya está fijo, no se valida del POST)
        if not all([username, email, tipo_documento, documento, password1, password2]):
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'registro.html', ctx)

        # Validar documento
        error_doc = _validar_documento(tipo_documento, documento)
        if error_doc:
            messages.error(request, error_doc)
            return render(request, 'registro.html', ctx)

        # Validar contraseña
        if len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'registro.html', ctx)

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html', ctx)

        # Verificar duplicados
        if Usuario.objects.filter(numero_documento=documento).exists():
            messages.error(request, 'Ya existe un usuario con ese número de documento.')
            return render(request, 'registro.html', ctx)

        if Usuario.objects.filter(correo=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return render(request, 'registro.html', ctx)

        # Crear usuario
        usuario = Usuario(
            numero_documento=documento,
            nombre_completo=username,
            correo=email,
            telefono='',
            tipo_documento=tipo_documento,
            password=make_password(password1),
            rol=rol_id,
        )

        try:
            usuario.full_clean()
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'registro.html', ctx)

        usuario.save()

        request.session['usuario_documento']      = usuario.numero_documento
        request.session['usuario_nombre']         = usuario.nombre_completo
        request.session['usuario_rol']            = usuario.rol
        request.session['usuario_tipo_documento'] = usuario.tipo_documento

        if usuario.rol.strip().lower() in ('administrador', 'instructor'):
            return redirect('home')
        return redirect('home_usuario')

    return render(request, 'registro.html', ctx_base)


# ─────────────────────────────────────────────────────────────
#  OLVIDÓ CONTRASEÑA
# ─────────────────────────────────────────────────────────────
def olvido_contrasena_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Ingresa tu correo electrónico.')
            return render(request, 'olvido_contrasena.html')

        try:
            usuario = Usuario.objects.get(correo=email)
        except Usuario.DoesNotExist:
            messages.success(request, 'Si el correo está registrado, recibirás un enlace.')
            return render(request, 'olvido_contrasena.html')

        token = get_random_string(40)
        request.session[f'reset_token_{usuario.numero_documento}'] = {
            'token':  token,
            'expira': time.time() + 900,
        }

        uid  = urlsafe_base64_encode(force_bytes(usuario.numero_documento))
        link = request.build_absolute_uri(
            reverse('nueva_contrasena', kwargs={'uid': uid, 'token': token})
        )

        try:
            send_mail(
                subject='Recuperación de contraseña – SENA Centro Minero',
                message=(
                    f'Hola {usuario.nombre_completo},\n\n'
                    f'Haz clic en el siguiente enlace para cambiar tu contraseña:\n\n{link}\n\n'
                    'Este enlace expira en 15 minutos.\n\n'
                    'Si no solicitaste esto, ignora este mensaje.\n\n'
                    'SENA – Centro Minero · Regional Boyacá'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Te enviamos un enlace a tu correo. Tienes 15 minutos para usarlo.')
        except Exception:
            messages.error(request, 'No se pudo enviar el correo. Contacta al administrador.')

    return render(request, 'olvido_contrasena.html')


# ─────────────────────────────────────────────────────────────
#  NUEVA CONTRASEÑA
# ─────────────────────────────────────────────────────────────
def nueva_contrasena_view(request, uid, token):
    try:
        documento = force_str(urlsafe_base64_decode(uid))
        usuario   = Usuario.objects.get(numero_documento=documento)
    except Exception:
        messages.error(request, 'El enlace no es válido.')
        return redirect('olvido_contrasena')

    data = request.session.get(f'reset_token_{documento}')
    if not data or data['token'] != token or time.time() > data['expira']:
        messages.error(request, 'El enlace ya fue usado o expiró. Solicita uno nuevo.')
        return redirect('olvido_contrasena')

    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'nueva_contrasena.html')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'nueva_contrasena.html')

        usuario.password = make_password(password1)
        usuario.save(update_fields=['password'])

        del request.session[f'reset_token_{documento}']
        messages.success(request, '¡Contraseña actualizada! Ya puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'nueva_contrasena.html')


# ─────────────────────────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────────────────────────
@sesion_requerida
@login_required
def home_view(request):
    rol = (request.session.get('usuario_rol') or '').strip().lower()
    if rol in ('administrador', 'admin'):
        return redirect('home')
    return redirect('home_usuario')


# ─────────────────────────────────────────────────────────────
#  LISTA DE USUARIOS  — solo Admin
# ─────────────────────────────────────────────────────────────
@admin_required
def lista_usuarios_view(request):
    qs = Usuario.objects.order_by('nombre_completo')

    q        = request.GET.get('q', '').strip()
    rol      = request.GET.get('rol', '')
    tipo_doc = request.GET.get('tipo_doc', '')

    if q:
        qs = qs.filter(
            Q(nombre_completo__icontains=q) |
            Q(numero_documento__icontains=q) |
            Q(correo__icontains=q)
        )
    if rol:
        qs = qs.filter(rol=rol)
    if tipo_doc:
        qs = qs.filter(tipo_documento=tipo_doc)

    ctx = {
        'usuarios':  qs,
        'roles':     ROLES,
        'tipos_doc': Usuario.TIPO_DOCUMENTO_CHOICES,
        'q':         q,
        'rol_id':    rol,
        'tipo_doc':  tipo_doc,
        'total':     qs.count(),
    }
    return render(request, 'lista_usuarios.html', ctx)


# ─────────────────────────────────────────────────────────────
#  DETALLE USUARIO (JSON para modal)
# ─────────────────────────────────────────────────────────────
@sesion_requerida
def detalle_usuario_json(request, numero_documento):
    usuario = get_object_or_404(
        Usuario.objects.select_related('destinado', 'solicitado'),
        numero_documento=numero_documento,
    )
    data = {
        'numero_documento':       usuario.numero_documento,
        'nombre_completo':        usuario.nombre_completo,
        'correo':                 usuario.correo,
        'telefono':               usuario.telefono,
        'tipo_documento_display': usuario.get_tipo_documento_display(),
        'rol':                    usuario.rol,
        'destinado':      usuario.destinado.nombre_completo if usuario.destinado else None,
        'destinado_doc':  usuario.destinado.numero_documento if usuario.destinado else None,
        'solicitado':     usuario.solicitado.nombre_completo if usuario.solicitado else None,
        'solicitado_doc': usuario.solicitado.numero_documento if usuario.solicitado else None,
    }
    return JsonResponse(data)


# ─────────────────────────────────────────────────────────────
#  EXPORTAR USUARIOS CSV
# ─────────────────────────────────────────────────────────────
@sesion_requerida
def exportar_usuarios_csv(request):
    qs = Usuario.objects.order_by('nombre_completo')

    q        = request.GET.get('q', '').strip()
    rol      = request.GET.get('rol', '')
    tipo_doc = request.GET.get('tipo_doc', '')

    if q:
        qs = qs.filter(
            Q(nombre_completo__icontains=q) |
            Q(numero_documento__icontains=q) |
            Q(correo__icontains=q)
        )
    if rol:
        qs = qs.filter(rol=rol)
    if tipo_doc:
        qs = qs.filter(tipo_documento=tipo_doc)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'
    response.write('\ufeff')  # BOM para Excel

    writer = csv.writer(response)
    writer.writerow(['Número de Documento', 'Tipo de Documento', 'Nombre Completo',
                     'Correo', 'Teléfono', 'Rol'])
    for u in qs:
        writer.writerow([
            u.numero_documento,
            u.get_tipo_documento_display(),
            u.nombre_completo,
            u.correo,
            u.telefono,
            u.rol,
        ])
    return response


# ─────────────────────────────────────────────────────────────
#  PERFIL
# ─────────────────────────────────────────────────────────────
@sesion_requerida
def perfil_view(request):
    doc     = request.session.get('usuario_documento')
    usuario = get_object_or_404(Usuario, numero_documento=doc)
    errores = {}
    accion_activa = ''

    if request.method == 'POST':
        accion_activa = request.POST.get('accion', '')

        # ── Editar datos personales ──────────────────────────────────
        if accion_activa == 'editar_perfil':
            nombre   = request.POST.get('nombre_completo', '').strip()
            correo   = request.POST.get('correo', '').strip().lower()
            telefono = request.POST.get('telefono', '').strip()

            if not nombre:
                errores['nombre_completo'] = 'El nombre no puede estar vacío.'
            if not correo or '@' not in correo:
                errores['correo'] = 'Ingresa un correo válido.'
            if telefono and not telefono.isdigit():
                errores['telefono'] = 'El teléfono solo debe contener dígitos.'
            if not errores.get('correo'):
                if Usuario.objects.filter(correo=correo).exclude(numero_documento=doc).exists():
                    errores['correo'] = 'Este correo ya está en uso por otro usuario.'

            if not errores:
                usuario.nombre_completo = nombre
                usuario.correo          = correo
                usuario.telefono        = telefono
                usuario.save(update_fields=['nombre_completo', 'correo', 'telefono'])
                request.session['usuario_nombre'] = nombre
                messages.success(request, 'Perfil actualizado correctamente.')
                return redirect('perfil')

        # ── Cambiar contraseña ───────────────────────────────────────
        elif accion_activa == 'cambiar_password':
            actual   = request.POST.get('password_actual', '')
            nueva    = request.POST.get('password_nueva', '')
            confirma = request.POST.get('password_confirma', '')

            if not check_password(actual, usuario.password):
                errores['password_actual'] = 'La contraseña actual es incorrecta.'
            if len(nueva) < 8:
                errores['password_nueva'] = 'La nueva contraseña debe tener al menos 8 caracteres.'
            if nueva != confirma:
                errores['password_confirma'] = 'Las contraseñas no coinciden.'

            if not errores:
                usuario.password = make_password(nueva)
                usuario.save(update_fields=['password'])
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('perfil')

        # ── Guardar configuración de notificaciones ──────────────────
        elif accion_activa == 'guardar_config':
            request.session['cfg_notif_prestamos']    = 'notif_prestamos'    in request.POST
            request.session['cfg_notif_vencimientos'] = 'notif_vencimientos' in request.POST
            request.session['cfg_notif_devoluciones'] = 'notif_devoluciones' in request.POST
            messages.success(request, 'Configuración guardada.')
            return redirect('perfil')

    cfg_notif_prestamos    = request.session.get('cfg_notif_prestamos',    True)
    cfg_notif_vencimientos = request.session.get('cfg_notif_vencimientos', True)
    cfg_notif_devoluciones = request.session.get('cfg_notif_devoluciones', True)

    return render(request, 'perfil.html', {
        'usuario':       usuario,
        'errores':       errores,
        'accion_activa': accion_activa,
        'tab_list': [
            ('tab-datos',    'Datos personales', ''),
            ('tab-password', 'Contraseña',       ''),
            ('tab-config',   'Notificaciones',   ''),
        ],
        'notificaciones_lista': [
            ('notif_prestamos',    'Nuevos préstamos asignados',
             'Recibir alerta cuando se te asigne un préstamo.',      cfg_notif_prestamos),
            ('notif_vencimientos', 'Próximos a vencer',
             'Alerta 3 días antes de que venza un préstamo activo.', cfg_notif_vencimientos),
            ('notif_devoluciones', 'Devoluciones pendientes',
             'Recordatorio de devoluciones en estado pendiente.',    cfg_notif_devoluciones),
        ],
        'cfg_notif_prestamos':    cfg_notif_prestamos,
        'cfg_notif_vencimientos': cfg_notif_vencimientos,
        'cfg_notif_devoluciones': cfg_notif_devoluciones,
    })