from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('home-usuario/', views.home_usuario_view, name='home_usuario'),
    path('prestamo-usuario/', views.prestamo_usuario_view, name='prestamo_usuario'),  # ← NUEVO
]