from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # Tipos de Estado 
    path('tipos-estado/',
         views.TipoEstadoListView.as_view(),
         name='tipo_estado_lista'),

    path('tipos-estado/nuevo/',
         views.TipoEstadoCreateView.as_view(),
         name='tipo_estado_nuevo'),

    path('tipos-estado/<int:pk>/editar/',
         views.TipoEstadoUpdateView.as_view(),
         name='tipo_estado_editar'),

    # Mantenimientos 
    path('',
         views.MantenimientoListView.as_view(),
         name='mantenimiento_lista'),

    path('<int:pk>/',
         views.MantenimientoDetailView.as_view(),
         name='mantenimiento_detalle'),

    path('<int:pk>/editar/',
         views.MantenimientoUpdateView.as_view(),
         name='mantenimiento_editar'),

    path('registrar-desde-inventario/',
         views.registrar_desde_inventario,
         name='registrar_desde_inventario'),

    # Estado actual y historial
    path('estado-actual/',
         views.EstadoActualListView.as_view(),
         name='estado_actual_lista'),

    path('historial/<int:producto_id>/',
         views.HistorialProductoView.as_view(),
         name='historial_producto'),
]