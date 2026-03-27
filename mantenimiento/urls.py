from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    path('consultar/',              views.consultar_tipo_estado, name='consultar_estado'),
    path('tipo-estado/',            views.tipo_estado_lista,     name='tipo_estado_lista'),
    path('tipo-estado/nuevo/',      views.tipo_estado_nuevo,     name='tipo_estado_nuevo'),
    path('tipo-estado/editar/<int:pk>/', views.tipo_estado_editar, name='tipo_estado_editar'),
]