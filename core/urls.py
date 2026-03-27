from django.contrib import admin
from django.urls import path, include
from usuario.views import iniciar_sesion
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pagina_principal.urls')),
    path('devoluciones/', include('devoluciones.urls')),
    path('usuario/', include('usuario.urls')),
    path('prestamos/', include('prestamo.urls')),
    path('inventario/', include('inventario.urls')),
    path('almacenamiento/', include('almacenamiento.urls')),  
    path('', iniciar_sesion, name='login'),
]
