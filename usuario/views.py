from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import Usuario, Rol


# ─────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────
def login_view(request):
    if request.session.get('usuario_documento'):
        return redirect('/mine/')

    if request.method == 'POST':
        documento = request.POST.get('documento', '').strip()
        password  = request.POST.get('password', '')

        if not documento or not password:
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'login.html')

        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                numero_documento=documento
            )
        except Usuario.DoesNotExist:
            messages.error(request, 'Número de documento o contraseña incorrectos.')
            return render(request, 'login.html')

        if not check_password(password, usuario.password):
            messages.error(request, 'Número de documento o contraseña incorrectos.')
            return render(request, 'login.html')

        # Guardar nombre completo en sesión
        request.session['usuario_documento'] = usuario.numero_documento
        request.session['usuario_nombre']    = usuario.nombre_completo
        request.session['usuario_rol']       = usuario.id_rol.nombre

        return redirect('/mine/')

    return render(request, 'login.html')


# ─────────────────────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────────────────────
def logout_view(request):
    request.session.flush()
    return redirect('/Usuario/login/')


# ─────────────────────────────────────────────────────────────
#  REGISTRO
# ─────────────────────────────────────────────────────────────
def registro_view(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip().lower()
        documento = request.POST.get('documento', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        ctx = {'username': username, 'email': email, 'documento': documento}

        if not all([username, email, documento, password1, password2]):
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'registro.html', ctx)

        if not documento.isdigit():
            messages.error(request, 'El número de documento solo debe contener dígitos.')
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

        # Crear rol por defecto si no existe
        rol_default, _ = Rol.objects.get_or_create(
            id=1,
            defaults={'nombre': 'Usuario'}
        )

        usuario = Usuario.objects.create(
            numero_documento=documento,
            nombre_completo=username,
            correo=email,
            telefono='',
            tipo_documento='CC',
            password=make_password(password1),
            id_rol=rol_default,
        )

        # Iniciar sesión automáticamente y redirigir a home
        request.session['usuario_documento'] = usuario.numero_documento
        request.session['usuario_nombre']    = usuario.nombre_completo
        request.session['usuario_rol']       = rol_default.nombre

        return redirect('/mine/')

    return render(request, 'registro.html', {
        'username': '', 'email': '', 'documento': ''
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