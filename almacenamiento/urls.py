from django.urls import path
from .views import crear_estante, vista_estantes

urlpatterns = [
    path('estante/crear/', crear_estante, name='crear_estante'),
    path('estantes/', vista_estantes, name='estantes'),
]