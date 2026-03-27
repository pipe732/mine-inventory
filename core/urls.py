from django.contrib import admin
from django.urls import path, include
from usuario.views import login_view as iniciar_sesion
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('pagina_principal.urls')),
    path('devoluciones/', include('devoluciones.urls')),
    path('mantenimiento/', include('mantenimiento.urls')), #agregamos el archivo mantenimiento
    path('usuario/', include('usuario.urls')),
    path('prestamos/', include('prestamo.urls')),
    path('inventario/', include('inventario.urls')),
    path('almacenamiento/', include('almacenamiento.urls')),  
    path('', iniciar_sesion, name='login'),
]
