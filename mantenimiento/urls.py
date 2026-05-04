# mantenimiento/urls.py
from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # TIPO DE MANTENIMIENTO
    # /mantenimiento/tipos-mantenimiento/
    path('tipos-mantenimiento/',
         views.TipoMantenimientoListView.as_view(),
         name='tipo_mantenimiento_lista'),
    
    # /mantenimiento/tipos-mantenimiento/crear/
    path('tipos-mantenimiento/crear/',
         views.TipoMantenimientoCreateView.as_view(),
         name='tipo_mantenimiento_crear'),
    
    # /mantenimiento/tipos-mantenimiento/<int:pk>/editar/
    path('tipos-mantenimiento/<int:pk>/editar/',
         views.TipoMantenimientoUpdateView.as_view(),
         name='tipo_mantenimiento_editar'),
    
    # /mantenimiento/tipos-mantenimiento/<int:pk>/inactivar/
    path('tipos-mantenimiento/<int:pk>/inactivar/',
         views.tipo_mantenimiento_inactivar,
         name='tipo_mantenimiento_inactivar'),
    
    # /mantenimiento/tipos-mantenimiento/<int:pk>/eliminar/
    path('tipos-mantenimiento/<int:pk>/eliminar/',
         views.tipo_mantenimiento_eliminar,
         name='tipo_mantenimiento_eliminar'),
    
    # TIPO DE ESTADO
    # /mantenimiento/tipo-estado/
    path('tipo-estado/',
         views.TipoEstadoListView.as_view(),
         name='tipo_estado_lista'),
    
    # /mantenimiento/tipo-estado/nuevo/
    path('tipo-estado/nuevo/',
         views.TipoEstadoCreateView.as_view(),
         name='tipo_estado_nuevo'),
    
    # /mantenimiento/tipo-estado/editar/<int:pk>/
    path('tipo-estado/editar/<int:pk>/',
         views.TipoEstadoUpdateView.as_view(),
         name='tipo_estado_editar'),

    # MANTENIMIENTO
    # /mantenimiento/
    path('',
         views.MantenimientoListView.as_view(),
         name='mantenimiento_lista'),
    
    # /mantenimiento/<int:pk>/
    path('<int:pk>/',
         views.MantenimientoDetailView.as_view(),
         name='mantenimiento_detalle'),

    # /mantenimiento/<int:pk>/editar/
    path('<int:pk>/editar/',
         views.MantenimientoUpdateView.as_view(),
         name='mantenimiento_editar'),

    # HISTORIAL
    # /mantenimiento/historial/<int:producto_id>/
    path('historial/<int:producto_id>/',
         views.HistorialProductoView.as_view(),
         name='historial_producto'),

    # ESTADO ACTUAL
    # /mantenimiento/estado-actual/
    path('estado-actual/',
         views.EstadoActualListView.as_view(),
         name='estado_actual_lista'),

    # DESDE INVENTARIO
    # /mantenimiento/registrar-desde-inventario/
    path('registrar-desde-inventario/',
         views.registrar_desde_inventario,
         name='registrar_desde_inventario'),
]