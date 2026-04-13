# mantenimiento/urls.py
from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # Estado actual
    path('estado-actual/',
         views.EstadoActualListView.as_view(),      
         name='estado_actual_lista'),

    # Catálogo tipos de estado
    path('tipo-estado/',
         views.TipoEstadoListView.as_view(),
         name='tipo_estado_lista'),
    path('tipo-estado/nuevo/',
         views.TipoEstadoCreateView.as_view(),
         name='tipo_estado_nuevo'),
    path('tipo-estado/editar/<int:pk>/',
         views.TipoEstadoUpdateView.as_view(),
         name='tipo_estado_editar'),

    # Mantenimiento
    path('',
         views.MantenimientoListView.as_view(),
         name='mantenimiento_lista'),
    path('nuevo/',
         views.MantenimientoCreateView.as_view(),
         name='mantenimiento_nuevo'),
    path('<int:pk>/editar/',
         views.MantenimientoUpdateView.as_view(),
         name='mantenimiento_editar'),
    path('<int:pk>/',
         views.MantenimientoDetailView.as_view(),
         name='mantenimiento_detalle'),

    # Historial
    path('historial/<int:producto_id>/',
         views.HistorialProductoView.as_view(),
         name='historial_producto'),

    # API AJAX — se queda como función, no necesita CBV
    path('api/productos/',
         views.api_buscar_producto,
         name='api_buscar_producto'),
]