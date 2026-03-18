# devoluciones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.devoluciones_view, name='devoluciones'),
]