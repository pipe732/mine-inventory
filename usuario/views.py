from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import PerfilUsuario


# Registro de usuario
def registro(request):
    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        documento = request.POST.get('documento')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        contexto_error = {
            'username': username,
            'email': email,
            'documento': documento
        }

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'usuario/registro.html', contexto_error)

        if len(password1) < 8:
            messages.error(request, "La contraseña debe tener mínimo 8 caracteres.")
            return render(request, 'usuario/registro.html', contexto_error)

        if User.objects.filter(username=documento).exists():
            messages.error(request, "Ya existe un usuario registrado con ese documento.")
            return render(request, 'usuario/registro.html', contexto_error)

        try:
            user = User.objects.create_user(username=documento, email=email, password=password1)
            user.first_name = username
            user.save()
            PerfilUsuario.objects.create(user=user, documento=documento)
            messages.success(request, "¡Usuario registrado correctamente! Ya puedes iniciar sesión.")
            return redirect('login')
        except Exception:
            messages.error(request, "Error al registrar. Intenta de nuevo.")
            return render(request, 'usuario/registro.html', contexto_error)

    return render(request, 'usuario/registro.html')


# Login de usuario
def iniciar_sesion(request):
    if request.method == "POST":
        documento = request.POST.get('documento')
        password = request.POST.get('password')

        user = authenticate(request, username=documento, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.first_name or documento}!")
            return redirect('inicio')
        else:
            messages.error(request, "Documento o contraseña incorrectos.")
            return render(request, 'usuario/login.html', {"documento": documento})

    return render(request, 'usuario/login.html')


# Olvido contraseña - solicitar correo
def olvido_contrasena(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            enlace = f"http://127.0.0.1:8000/nueva-contrasena/{uid}/{token}/"

            send_mail(
                subject="Recuperar contraseña - Centro Minero SENA",
                message=f"Hola {user.first_name},\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n\n{enlace}\n\nSi no solicitaste esto, ignora este correo.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(request, "Te enviamos un enlace a tu correo. Revisa tu bandeja de entrada.")
        except User.DoesNotExist:
            messages.success(request, "Te enviamos un enlace a tu correo. Revisa tu bandeja de entrada.")

        return render(request, 'usuario/olvido_contrasena.html')

    return render(request, 'usuario/olvido_contrasena.html')


# Nueva contraseña - restablecer
def nueva_contrasena(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace no es válido o ha expirado.")
        return redirect('olvido_contrasena')

    if request.method == "POST":
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'usuario/nueva_contrasena.html', {'uidb64': uidb64, 'token': token})

        if len(password1) < 8:
            messages.error(request, "La contraseña debe tener mínimo 8 caracteres.")
            return render(request, 'usuario/nueva_contrasena.html', {'uidb64': uidb64, 'token': token})

        user.set_password(password1)
        user.save()
        messages.success(request, "¡Contraseña actualizada correctamente! Ya puedes iniciar sesión.")
        return redirect('login')

    return render(request, 'usuario/nueva_contrasena.html', {'uidb64': uidb64, 'token': token})