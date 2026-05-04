# mantenimiento/urls.py
from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # TIPO DE MANTENIMIENTO
    path('tipos-mantenimiento/',
         views.TipoMantenimientoListView.as_view(),
         name='tipo_mantenimiento_lista'),
    
    path('tipos-mantenimiento/crear/',
         views.TipoMantenimientoCreateView.as_view(),
         name='tipo_mantenimiento_crear'),
    
    path('tipos-mantenimiento/<int:pk>/editar/',
         views.TipoMantenimientoUpdateView.as_view(),
         name='tipo_mantenimiento_editar'),
    
    path('tipos-mantenimiento/<int:pk>/inactivar/',
         views.tipo_mantenimiento_inactivar,
         name='tipo_mantenimiento_inactivar'),
    
    path('tipos-mantenimiento/<int:pk>/eliminar/',
         views.tipo_mantenimiento_eliminar,
         name='tipo_mantenimiento_eliminar'),
    
    # TIPO DE ESTADO
    path('tipo-estado/',
         views.TipoEstadoListView.as_view(),
         name='tipo_estado_lista'),
    
    path('tipo-estado/nuevo/',
         views.TipoEstadoCreateView.as_view(),
         name='tipo_estado_nuevo'),
    
    path('tipo-estado/editar/<int:pk>/',
         views.TipoEstadoUpdateView.as_view(),
         name='tipo_estado_editar'),

    # MANTENIMIENTO
    path('',
         views.MantenimientoListView.as_view(),
         name='mantenimiento_lista'),
    
    path('<int:pk>/',
         views.MantenimientoDetailView.as_view(),
         name='mantenimiento_detalle'),

    path('<int:pk>/editar/',
         views.MantenimientoUpdateView.as_view(),
         name='mantenimiento_editar'),

    # HISTORIAL
    path('historial/<int:producto_id>/',
         views.HistorialProductoView.as_view(),
         name='historial_producto'),

    # ESTADO ACTUAL
    path('estado-actual/',
         views.EstadoActualListView.as_view(),
         name='estado_actual_lista'),

    # DESDE INVENTARIO
    path('registrar-desde-inventario/',
         views.registrar_desde_inventario,
         name='registrar_desde_inventario'),
]