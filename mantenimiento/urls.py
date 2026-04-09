from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    
    path('estado-actual/',
         views.estado_actual_lista,
         name='estado_actual_lista'),
    
    # ── Catálogo de tipos de estado ───────────────────────────
    path('tipo-estado/',
         views.tipo_estado_lista,
         name='tipo_estado_lista'),
    path('tipo-estado/nuevo/',
         views.tipo_estado_nuevo,
         name='tipo_estado_nuevo'),
    path('tipo-estado/editar/<int:pk>/',
         views.tipo_estado_editar,
         name='tipo_estado_editar'),

    # ── Registros de mantenimiento ────────────────────────────
    path('',
         views.mantenimiento_lista,
         name='mantenimiento_lista'),
    path('nuevo/',
         views.mantenimiento_nuevo,
         name='mantenimiento_nuevo'),
    path('<int:pk>/editar/',
         views.mantenimiento_editar,
         name='mantenimiento_editar'),
    path('<int:pk>/',
         views.mantenimiento_detalle,
         name='mantenimiento_detalle'),

    # ── API AJAX ──────────────────────────────────────────────
    path('api/productos/',
         views.api_buscar_producto,
         name='api_buscar_producto'),
    
    # Dentro de urlpatterns = [ ... ]

    path('historial/<int:producto_id>/', 
         views.mantenimiento_historial_producto, 
         name='historial_producto'),
]