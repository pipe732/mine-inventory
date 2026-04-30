from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.inventario, name='inventario'),
    path('productos/autocomplete/', views.producto_autocomplete, name='producto_autocomplete'),
]