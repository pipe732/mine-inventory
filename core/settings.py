"""
Django settings for core project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────
#  SEGURIDAD
# ─────────────────────────────────────────────────────────────
# ADVERTENCIA: cambia esta clave en producción y nunca la publiques
SECRET_KEY = 'django-insecure-)1t4q$yd=#qejd0tu*58*n89e8i^(=)&*=5()7it#l0b997(w^'

DEBUG = True

ALLOWED_HOSTS = ['*']


# ─────────────────────────────────────────────────────────────
#  APLICACIONES
# ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'devoluciones',
    'usuario',
    'prestamo',
    'inventario',
    'almacenamiento',
    'pagina_principal',
    'mantenimiento',
    'reportes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# ─────────────────────────────────────────────────────────────
#  BASE DE DATOS
# ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ─────────────────────────────────────────────────────────────
#  VALIDACIÓN DE CONTRASEÑAS
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────────────────────────
#  INTERNACIONALIZACIÓN
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-co'   # ✅ cambiado a español Colombia

TIME_ZONE = 'America/Bogota'  # ✅ zona horaria correcta

USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────────────────────────
#  ARCHIVOS ESTÁTICOS Y MEDIA
# ─────────────────────────────────────────────────────────────
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ─────────────────────────────────────────────────────────────
#  SESIONES
# ─────────────────────────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600          # sesión expira en 1 hora (segundos)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # cierra sesión al cerrar el navegador


# ─────────────────────────────────────────────────────────────
#  REDIRECCIONES DE AUTH  ✅ corregidas
# ─────────────────────────────────────────────────────────────
LOGIN_URL = '/'               # si no está logueado, va al login (ruta raíz)
LOGIN_REDIRECT_URL = '/home/' # después de login exitoso, va a home
LOGOUT_REDIRECT_URL = '/'     # después de logout, vuelve al login


# ─────────────────────────────────────────────────────────────
#  CORREO (configura con tus credenciales reales)
# ─────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tucorreo@gmail.com'       # ← cambia esto
EMAIL_HOST_PASSWORD = 'tu_contraseña_app'    # ← cambia esto
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ─────────────────────────────────────────────────────────────
#  CAMPO PK POR DEFECTO
# ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Permite que JS lea la cookie CSRF
CSRF_COOKIE_HTTPONLY = False