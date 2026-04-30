from django.urls import path
from . import views

urlpatterns = [
    path('',        views.reportes_view,        name='reportes'),
    path('generar/', views.generar_reporte_view, name='generar_reporte'),
]