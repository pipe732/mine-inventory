import re
import os
import sys
import subprocess
from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from usuario.decorators import admin_required
from .models import ConfiguracionSistema


ENV_PATH = Path(__file__).resolve().parent.parent / '.env'

import re
from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from usuario.decorators import admin_required

ENV_PATH = Path(__file__).resolve().parent.parent / '.env'


def _leer_env(clave: str, default: str = '') -> str:
    """Lee el valor actual de una clave en el .env."""
    if not ENV_PATH.exists():
        return default
    contenido = ENV_PATH.read_text(encoding='utf-8')
    patron = re.compile(rf'^{re.escape(clave)}\s*=\s*(.+)$', re.MULTILINE)
    match = patron.search(contenido)
    return match.group(1).strip() if match else default


def _actualizar_env(clave: str, valor: str):
    """Reemplaza o agrega una clave en el archivo .env."""
    if not ENV_PATH.exists():
        ENV_PATH.write_text(f'{clave}={valor}\n', encoding='utf-8')
        return

    contenido = ENV_PATH.read_text(encoding='utf-8')
    patron = re.compile(rf'^{re.escape(clave)}\s*=.*$', re.MULTILINE)

    if patron.search(contenido):
        nuevo = patron.sub(f'{clave}={valor}', contenido)
    else:
        nuevo = contenido.rstrip('\n') + f'\n{clave}={valor}\n'

    ENV_PATH.write_text(nuevo, encoding='utf-8')


def _forzar_recarga():
    """Toca settings.py y views.py para forzar recarga del runserver."""
    base = Path(__file__).resolve().parent.parent
    for path in [
        base / 'core' / 'settings.py',
        Path(__file__).resolve(),
    ]:
        if path.exists():
            path.touch()


@admin_required
def configuracion_view(request):
  
    almacenamiento_actual = _leer_env('DB_ENGINE', default='nube')

    if request.method == 'POST':
        almacenamiento = request.POST.get('almacenamiento', 'nube')

        _actualizar_env('DB_ENGINE', almacenamiento)
        _forzar_recarga()

        # Cierra sesión para que el admin entre con la nueva BD activa
        request.session.flush()

        nombre_bd = 'Local (SQLite)' if almacenamiento == 'local' else 'Nube (Neon PostgreSQL)'
        messages.success(
            request,
            f' Base de datos cambiada a {nombre_bd}. '
            'Espera 3 segundos e inicia sesión nuevamente.'
        )
        return redirect('login')
    class Config:
        pass

    config = Config()
    config.almacenamiento = almacenamiento_actual

    return render(request, 'configuracion.html', {'config': config})


@admin_required
@require_GET
def probar_conexion_neon(request):
    try:
        import psycopg2
        from decouple import config as env
        conn = psycopg2.connect(
            dbname=env('DB_NAME'),
            user=env('DB_USER'),
            password=env('DB_PASSWORD'),
            host=env('DB_HOST'),
            port=env('DB_PORT', default='5432'),
            connect_timeout=5,
            sslmode='require',
        )
        conn.close()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})