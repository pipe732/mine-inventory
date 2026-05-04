from django.urls import path
from . import views

# ✅ Correcto
"""
Linea comentada temporal
urlpatterns = [
    path('admin/', views.dashboard_view, name='home'),
    path('usuario/', views.home_usuario_view, name='home_usuario'),
]
"""
urlpatterns = [
    path('admin/', views.dashboard_view, name='home'),
]