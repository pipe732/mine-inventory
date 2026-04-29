# prestamo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.prestamos_view, name='prestamo'),
    path('<int:pk>/api/', views.prestamo_api, name='prestamo_api'),
    path('<int:pk>/aprobar/', views.aprobar_prestamo_view, name='aprobar_prestamo'),
    path('usuario/', views.prestamo_usuario_view, name='prestamo_usuario'),
    path('usuario/solicitar/', views.usuario_solicitar_prestamo, name='usuario_solicitar_prestamo'),
]