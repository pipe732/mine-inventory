# prestamos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.prestamos_view, name='prestamo'),
]