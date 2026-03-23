from django.urls import path
from . import views
app_name = 'mantenimiento'
urlpatterns = [
    #Conectamos la url de la funcion que se creo en views.py
    path('consultar-estado/', views.consultar_tipo_estado, name='consultar_estado'),
    path('tipo-estado/nuevo/',  views.TipoEstadoCreateView.as_view(), name='tipo_estado_nuevo'),
]