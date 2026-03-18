from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('devoluciones/', include('devoluciones.urls')),
    path('mantenimiento/', include('mantenimiento.urls')), #agregamos el archivo mantenimiento
]
