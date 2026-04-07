from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuario.views import login_view
from prestamo.views import prestamo_api  # ← nueva

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('home/', include('pagina_principal.urls')),
    path('devoluciones/', include('devoluciones.urls')),
    path('usuario/', include('usuario.urls')),
    path('prestamos/', include('prestamo.urls')),
    path('inventario/', include('inventario.urls')),
    path('almacenamiento/', include('almacenamiento.urls')),
    path('mantenimiento/', include('mantenimiento.urls')),
    path('reportes/', include('reportes.urls')),
    path('api/prestamos/<int:pk>/', prestamo_api, name='api_prestamo'),  # ← nueva
]