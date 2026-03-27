from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    #Consultar estados de herramienta: http://127.0.0.1:8000/mantenimiento/consultar-estado/
    path('consultar-estado/', views.consultar_tipo_estado, name='consultar_estado'),

    #Crear y editar tipos de estado: http://127.0.0.1:8000/mantenimiento/tipo-estado/
    path('tipo-estado/nuevo/', views.tipo_estado_nuevo, name='tipo_estado_nuevo'),

    #Crear nuevo tipo de estado: http://127.0.0.1:8000/mantenimiento/tipo-estado/nuevo/ 
    path('tipo-estado/', views.tipo_estado_lista, name='tipo_estado_lista'),

    #Editar tipo de estado: http://127.0.0.1:8000/mantenimiento/tipo-estado/editar/1/
    path('tipo-estado/editar/<int:pk>/', views.tipo_estado_editar, name='tipo_estado_editar'),
    
    #Registrar mantenimiento: 
]