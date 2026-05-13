from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.dashboard_view, name='home'),
    path('usuario/', views.home_usuario_view, name='home_usuario'),
    path('notificaciones/',  views.notificaciones_json,    name='notificaciones_json'),
]