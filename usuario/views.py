import re
import time
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import Usuario, Rol, validar_numero_documento
from django.core.exceptions import ValidationError

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

        if not all([tipo_documento, documento, password]):
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'login.html', {'tipo_documento': tipo_documento, 'documento': documento})

        error_doc = _validar_documento(tipo_documento, documento)
        if error_doc:
            messages.error(request, error_doc)
            return render(request, 'login.html', {'tipo_documento': tipo_documento, 'documento': documento})

        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                numero_documento=documento,
                tipo_documento=tipo_documento,
            )
        except Usuario.DoesNotExist:
            messages.error(request, 'Documento o contraseña incorrectos.')
            return render(request, 'login.html', {'tipo_documento': tipo_documento, 'documento': documento})

        if not check_password(password, usuario.password):
            messages.error(request, 'Documento o contraseña incorrectos.')
            return render(request, 'login.html', {'tipo_documento': tipo_documento, 'documento': documento})

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

        ctx = {'username': username, 'email': email, 'tipo_documento': tipo_documento, 'documento': documento}

        if not all([username, email, tipo_documento, documento, password1, password2]):
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'registro.html', ctx)

        error_doc = _validar_documento(tipo_documento, documento)
        if error_doc:
            messages.error(request, error_doc)
            return render(request, 'registro.html', ctx)

        if len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'registro.html', ctx)

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html', ctx)

        if Usuario.objects.filter(numero_documento=documento).exists():
            messages.error(request, 'Ya existe un usuario con ese número de documento.')
            return render(request, 'registro.html', ctx)

        if Usuario.objects.filter(correo=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return render(request, 'registro.html', ctx)

        rol_default, _ = Rol.objects.get_or_create(id=1, defaults={'nombre': 'Usuario'})
        usuario = Usuario(
            numero_documento=documento,
            nombre_completo=username,
            correo=email,
            telefono='',
            tipo_documento=tipo_documento,
            password=make_password(password1),
            id_rol=rol_default,
        )

        try:
            usuario.full_clean()
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'registro.html', ctx)

        usuario.save()
        request.session['usuario_documento']      = usuario.numero_documento
        request.session['usuario_nombre']         = usuario.nombre_completo
        request.session['usuario_rol']            = rol_default.nombre
        request.session['usuario_tipo_documento'] = usuario.tipo_documento
        return redirect('home')

    return render(request, 'registro.html', {'username': '', 'email': '', 'tipo_documento': 'CC', 'documento': ''})


# ─────────────────────────────────────────────────────────────
#  OLVIDÓ CONTRASEÑA — envía el link
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
            messages.success(request, 'Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.')
            return render(request, 'olvido_contrasena.html')

        # Genera token y lo guarda en sesión con expiración de 15 minutos
        token = get_random_string(40)
        request.session[f'reset_token_{usuario.numero_documento}'] = {
            'token': token,
            'expira': time.time() + 900  # 15 minutos en segundos
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
#  NUEVA CONTRASEÑA — formulario desde el link
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

        # Invalida el token para que no se reutilice
        del request.session[f'reset_token_{documento}']

        messages.success(request, '¡Contraseña actualizada! Ya puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'nueva_contrasena.html')