from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuario.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # ✅ Ruta raíz → muestra el login directamente al abrir el servidor
    path('', login_view, name='login'),
    path('home/', include('pagina_principal.urls')),
    path('devoluciones/', include('devoluciones.urls')),
    path('usuario/', include('usuario.urls')),
    path('prestamos/', include('prestamo.urls')),
    path('inventario/', include('inventario.urls')),
    path('almacenamiento/', include('almacenamiento.urls')),
    path('mantenimiento/', include('mantenimiento.urls')),
] 