from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('devoluciones/', include('devoluciones.urls')),
    path('usuario/', include('usuario.urls')),
    path('prestamos/', include('prestamo.urls')),
    path('inventario/', include('inventario.urls')),
    path('almacenamiento/', include('almacenamiento.urls')),  
]
