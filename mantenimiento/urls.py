from django.urls import path
from . import views

urlpatterns = [
    #Conectamos la url de la funcion que se creo en views.py
    path('consultar-estado/', views.consultar_tipo_estado, name='consultar_estado'),
]