from django.urls import path
from . import views

# ✅ Correcto
urlpatterns = [
    path('', views.dashboard_view, name='home'),
]