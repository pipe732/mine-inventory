from django.urls import path
from . import views

urlpatterns = [
    path('',         views.login_view,            name='login'),
    path('login/',   views.login_view,            name='login'),
    path('logout/',  views.logout_view,           name='logout'),
    path('registro/', views.registro_view,        name='registro'),
    path('olvido/',  views.olvido_contrasena_view, name='olvido_contrasena'),
]