# usuario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.login_view,            name='login'),
    path('logout/',                                 views.logout_view,           name='logout'),
    path('registro/',                               views.registro_view,         name='registro'),
    path('olvido/',                                 views.olvido_contrasena_view,name='olvido_contrasena'),
    path('nueva-contrasena/<uid>/<token>/',         views.nueva_contrasena_view, name='nueva_contrasena'),
    # Gestión de usuarios
    path('usuarios/',                               views.lista_usuarios_view,   name='lista_usuarios'),
    path('usuarios/<str:numero_documento>/json/',   views.detalle_usuario_json,  name='detalle_usuario_json'),
    # Perfil propio
    path('perfil/',                                 views.perfil_view,           name='perfil'),
]