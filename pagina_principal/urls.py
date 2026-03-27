from django.urls import path
from . import views

urlpatterns = [
    # Esta ruta define la página de inicio (vacía '') 
    # que llama a la función dashboard_view de tu views.py
    path('', views.dashboard_view, name='dashboard'),
]