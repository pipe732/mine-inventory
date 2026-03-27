import re
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import Usuario, Rol, validar_numero_documento
from django.core.exceptions import ValidationError


# ── Reglas de documento (espejo del frontend) ────────────────────────────────
DOC_RULES = {
    'CC': re.compile(r'^\d{6,10}$'),
    'CE': re.compile(r'^[A-Za-z0-9]{6,12}$'),
    'PP': re.compile(r'^[A-Za-z0-9]{5,9}$'),
    'TI': re.compile(r'^\d{10,11}$'),
}
DOC_LABELS = {
    'CC': 'Cédula de Ciudadanía',
    'CE': 'Cédula de Extranjería',
    'PP': 'Pasaporte',
    'TI': 'Tarjeta de Identidad',
}
DOC_HINTS = {
    'CC': 'La Cédula de Ciudadanía debe tener entre 6 y 10 dígitos.',
    'CE': 'La Cédula de Extranjería debe tener entre 6 y 12 caracteres alfanuméricos.',
    'PP': 'El Pasaporte debe tener entre 5 y 9 caracteres alfanuméricos.',
    'TI': 'La Tarjeta de Identidad debe tener 10 u 11 dígitos.',
}

TIPOS_VALIDOS = set(DOC_RULES.keys())


def _validar_documento(tipo, numero):
    """Devuelve None si es válido, o un string con el error."""
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

        # ── Validaciones básicas ──────────────────────────────
        if not all([tipo_documento, documento, password]):
            messages.error(request, 'Completa todos los campos.')
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

        # ── Buscar usuario por documento Y tipo ───────────────
        try:
            usuario = Usuario.objects.select_related('id_rol').get(
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

        # ── Sesión ────────────────────────────────────────────
        request.session['usuario_documento']      = usuario.numero_documento
        request.session['usuario_nombre']         = usuario.nombre_completo
        request.session['usuario_rol']            = usuario.id_rol.nombre
        request.session['usuario_tipo_documento'] = usuario.tipo_documento

        return redirect('home')

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
    if request.method == 'POST':
        username       = request.POST.get('username', '').strip()
        email          = request.POST.get('email', '').strip().lower()
        tipo_documento = request.POST.get('tipo_documento', '').strip().upper()
        documento      = request.POST.get('documento', '').strip()
        password1      = request.POST.get('password1', '')
        password2      = request.POST.get('password2', '')

        ctx = {
            'username':       username,
            'email':          email,
            'tipo_documento': tipo_documento,
            'documento':      documento,
        }

        # ── Campos vacíos ─────────────────────────────────────
        if not all([username, email, tipo_documento, documento, password1, password2]):
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'registro.html', ctx)

        # ── Formato de documento ──────────────────────────────
        error_doc = _validar_documento(tipo_documento, documento)
        if error_doc:
            messages.error(request, error_doc)
            return render(request, 'registro.html', ctx)

        # ── Contraseña ────────────────────────────────────────
        if len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'registro.html', ctx)

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html', ctx)

        # ── Unicidad ──────────────────────────────────────────
        if Usuario.objects.filter(numero_documento=documento).exists():
            messages.error(request, 'Ya existe un usuario con ese número de documento.')
            return render(request, 'registro.html', ctx)

        if Usuario.objects.filter(correo=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return render(request, 'registro.html', ctx)

        # ── Crear usuario ─────────────────────────────────────
        rol_default, _ = Rol.objects.get_or_create(
            id=1,
            defaults={'nombre': 'Usuario'}
        )

        usuario = Usuario(
            numero_documento=documento,
            nombre_completo=username,
            correo=email,
            telefono='',
            tipo_documento=tipo_documento,
            password=make_password(password1),
            id_rol=rol_default,
        )

        # Validación a nivel de modelo (llama a clean())
        try:
            usuario.full_clean()
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'registro.html', ctx)

        usuario.save()

        # ── Sesión automática ─────────────────────────────────
        request.session['usuario_documento']      = usuario.numero_documento
        request.session['usuario_nombre']         = usuario.nombre_completo
        request.session['usuario_rol']            = rol_default.nombre
        request.session['usuario_tipo_documento'] = usuario.tipo_documento

        return redirect('home')

    return render(request, 'registro.html', {
        'username': '', 'email': '', 'tipo_documento': 'CC', 'documento': ''
    })


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
            # Respuesta genérica para no revelar si el correo existe
            messages.success(
                request,
                'Si el correo está registrado, recibirás una contraseña temporal.'
            )
            return render(request, 'olvido_contrasena.html')

        nueva_pass = get_random_string(10)
        usuario.password = make_password(nueva_pass)
        usuario.save(update_fields=['password'])

        try:
            send_mail(
                subject='Recuperación de contraseña – SENA Centro Minero',
                message=(
                    f'Hola {usuario.nombre_completo},\n\n'
                    f'Tu contraseña temporal es: {nueva_pass}\n\n'
                    'Por seguridad, cámbiala después de iniciar sesión.\n\n'
                    'SENA – Centro Minero · Regional Boyacá'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Se envió una contraseña temporal a tu correo.')
        except Exception:
            messages.error(request, 'No se pudo enviar el correo. Contacta al administrador.')

    return render(request, 'olvido_contrasena.html')