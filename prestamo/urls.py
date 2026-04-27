# prestamo/urls.py
from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.prestamos_view, name='prestamo'),
    path('<int:pk>/api/', views.prestamo_api, name='prestamo_api'),
    path('usuario/solicitar/', views.usuario_solicitar_prestamo, name='usuario_solicitar_prestamo'),  # ← NUEVO
]