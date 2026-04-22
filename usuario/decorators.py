from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def login_required(view_func):
    """Redirige al login si no hay sesión activa."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            messages.error(request, 'Debes iniciar sesión para acceder.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Solo permite acceso a usuarios con rol 'Admin'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            messages.error(request, 'Debes iniciar sesión para acceder.')
            return redirect('login')
        if request.session.get('usuario_rol', '').lower() != 'admin':
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def usuario_required(view_func):
    """Permite acceso solo a usuarios con rol 'Usuario' o 'Admin'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            messages.error(request, 'Debes iniciar sesión para acceder.')
            return redirect('login')
        rol = request.session.get('usuario_rol', '').lower()
        if rol not in ('admin', 'usuario'):
            messages.error(request, 'No tienes permisos para acceder.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
