from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from .models import EstadoHerramienta, TipoEstado, Mantenimiento
from .forms import TipoEstadoForm, MantenimientoForm
from inventario.models import Producto


# ══════════════════════════════════════════════
# DECORADOR DE SESIÓN
# ══════════════════════════════════════════════

def login_requerido(view_func):
    """Decorador simple que usa tu sistema de sesiones."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_requerido
def tipo_estado_lista(request):
    estados = TipoEstado.objects.all().order_by('nombre')
    return render(request, 'mantenimiento/tipo_estado_list.html', {'estados': estados})


@login_requerido
def tipo_estado_nuevo(request):
    if request.method == 'POST':
        form = TipoEstadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de estado "{form.cleaned_data["nombre"]}" registrado correctamente.')
            return redirect('mantenimiento:tipo_estado_lista')
    else:
        form = TipoEstadoForm()

    return render(request, 'mantenimiento/tipo_estado_form.html', {
        'form': form,
        'title': 'Nuevo Tipo de Estado',
        'subtitle': 'Agrega un nuevo estado al catálogo de mantenimiento',
        'form_section_title': 'Datos del estado',
        'boton_texto': 'Guardar Tipo de Estado',
    })


@login_requerido
def tipo_estado_editar(request, pk):
    tipo_estado = get_object_or_404(TipoEstado, pk=pk)

    if request.method == 'POST':
        form = TipoEstadoForm(request.POST, instance=tipo_estado)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de estado "{tipo_estado.nombre}" actualizado correctamente.')
            return redirect('mantenimiento:tipo_estado_lista')
    else:
        form = TipoEstadoForm(instance=tipo_estado)

    return render(request, 'mantenimiento/tipo_estado_form.html', {
        'form': form,
        'title': 'Editar Tipo de Estado',
        'subtitle': 'Modifica los datos del estado seleccionado',
        'form_section_title': 'Modificar datos del estado',
        'boton_texto': 'Guardar Cambios',
    })


# ══════════════════════════════════════════════
# VISTAS NUEVAS — Mantenimiento
# ══════════════════════════════════════════════

@login_requerido
def mantenimiento_lista(request):
    """Lista todos los registros de mantenimiento con filtros."""
    registros = Mantenimiento.objects.select_related(
        'producto', 'tipo_estado', 'responsable'
    ).order_by('-fecha_reporte')

    q             = request.GET.get('q', '')
    tipo_filtro   = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado_registro', '')

    if q:
        registros = registros.filter(
            Q(producto__nombre__icontains=q) |
            Q(producto__codigo_sku__icontains=q) |
            Q(descripcion_problema__icontains=q)
        )
    if tipo_filtro:
        registros = registros.filter(tipo_mantenimiento=tipo_filtro)
    if estado_filtro:
        registros = registros.filter(estado_registro=estado_filtro)

    return render(request, 'mantenimiento/mantenimiento_lista.html', {
        'registros': registros,
        'tipo_choices': Mantenimiento.TIPO_CHOICES,
        'estado_choices': Mantenimiento.ESTADO_REGISTRO_CHOICES,
        'q': q,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
    })


@login_requerido
def mantenimiento_nuevo(request):
    """Registra un nuevo mantenimiento."""
    producto_inicial = request.GET.get('producto')

    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save(commit=False)

            # Auditoría: usuario que crea el registro
            if request.session.get('usuario_documento'):
                from django.contrib.auth.models import User
                try:
                    mantenimiento.creado_por = User.objects.get(
                        username=request.session['usuario_documento']
                    )
                except User.DoesNotExist:
                    pass

            mantenimiento.save()

            messages.success(
                request,
                f'Mantenimiento registrado correctamente para '
                f'[{mantenimiento.producto.codigo_sku}] {mantenimiento.producto.nombre} '
                f'— Estado: {mantenimiento.tipo_estado.nombre}.'
            )
            return redirect('mantenimiento:mantenimiento_lista')
    else:
        initial = {}
        if producto_inicial:
            initial['producto'] = producto_inicial
        form = MantenimientoForm(initial=initial)

    return render(request, 'mantenimiento/mantenimiento_form.html', {
        'form': form,
        'title': 'Nuevo Mantenimiento',
        'subtitle': 'Registra un mantenimiento correctivo o preventivo',
        'boton_texto': 'Registrar Mantenimiento',
    })


@login_requerido
def mantenimiento_editar(request, pk):
    """Edita un registro de mantenimiento existente."""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)

    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=mantenimiento)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Mantenimiento de [{mantenimiento.producto.codigo_sku}] '
                f'{mantenimiento.producto.nombre} actualizado correctamente.'
            )
            return redirect('mantenimiento:mantenimiento_lista')
    else:
        form = MantenimientoForm(instance=mantenimiento)

    return render(request, 'mantenimiento/mantenimiento_form.html', {
        'form': form,
        'mantenimiento': mantenimiento,
        'title': 'Editar Mantenimiento',
        'subtitle': 'Modifica los datos del registro de mantenimiento',
        'boton_texto': 'Guardar Cambios',
    })


@login_requerido
def mantenimiento_detalle(request, pk):
    """Vista de detalle de un mantenimiento."""
    mantenimiento = get_object_or_404(
        Mantenimiento.objects.select_related(
            'producto', 'tipo_estado', 'responsable', 'creado_por'
        ),
        pk=pk
    )
    return render(request, 'mantenimiento/mantenimiento_detalle.html', {
        'm': mantenimiento,
    })


# ══════════════════════════════════════════════
# API AJAX — Autocompletado de productos
# ══════════════════════════════════════════════

@login_requerido
def api_buscar_producto(request):
    """
    Endpoint AJAX para el autocompletado del formulario.
    GET /mantenimiento/api/productos/?q=taladro
    """
    q = request.GET.get('q', '').strip()
    resultados = []

    if len(q) >= 2:
        productos = Producto.objects.filter(
            Q(nombre__icontains=q) |
            Q(codigo_sku__icontains=q) |
            Q(numero_serie__icontains=q)
        )[:10]

        for p in productos:
            resultados.append({
                'id': p.pk,
                'texto': f"[{p.codigo_sku}] {p.nombre}",
                'codigo_sku': p.codigo_sku,
                'nombre': p.nombre,
                'ubicacion': p.ubicacion or '—',
                'disponible': p.disponible,
            })

    return JsonResponse({'resultados': resultados})

@login_requerido
def estado_actual_lista(request):
    """Vista moderna para consultar el estado ACTUAL de todas las herramientas/productos"""
    
    q = request.GET.get('q', '').strip()
    disponible_filtro = request.GET.get('disponible', '')

    # Query base con información del último mantenimiento
    productos = Producto.objects.prefetch_related('mantenimientos').order_by('nombre')

    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) |
            Q(codigo_sku__icontains=q) |
            Q(numero_serie__icontains=q) |
            Q(ubicacion__icontains=q)
        )

    if disponible_filtro:
        if disponible_filtro == 'si':
            productos = productos.filter(disponible=True)
        elif disponible_filtro == 'no':
            productos = productos.filter(disponible=False)

    # Para cada producto obtenemos el último mantenimiento (en la plantilla)
    context = {
        'productos': productos,
        'q': q,
        'disponible_filtro': disponible_filtro,
        'total_disponibles': Producto.objects.filter(disponible=True).count(),
        'total_no_disponibles': Producto.objects.filter(disponible=False).count(),
    }

    return render(request, 'mantenimiento/estado_actual.html', context)

# ══════════════════════════════════════════════
# VISTA DE HISTORIAL POR ACTIVO / PRODUCTO
# ══════════════════════════════════════════════

@login_requerido
def mantenimiento_historial_producto(request, producto_id):
    """Historial completo de mantenimientos de un solo ítem/activo."""
    producto = get_object_or_404(Producto, pk=producto_id)

    mantenimientos = Mantenimiento.objects.filter(
        producto=producto
    ).select_related(
        'tipo_estado', 'responsable', 'creado_por'
    ).order_by('-fecha_reporte')

    # Filtros
    q = request.GET.get('q', '').strip()
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado_registro', '')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if q:
        mantenimientos = mantenimientos.filter(
            Q(descripcion_problema__icontains=q) |
            Q(acciones_realizadas__icontains=q)
        )

    if tipo_filtro:
        mantenimientos = mantenimientos.filter(tipo_mantenimiento=tipo_filtro)

    if estado_filtro:
        mantenimientos = mantenimientos.filter(estado_registro=estado_filtro)

    if fecha_desde:
        mantenimientos = mantenimientos.filter(fecha_reporte__gte=fecha_desde)
    if fecha_hasta:
        mantenimientos = mantenimientos.filter(fecha_reporte__lte=fecha_hasta)

    context = {
        'producto': producto,
        'mantenimientos': mantenimientos,
        'tipo_choices': Mantenimiento.TIPO_CHOICES,
        'estado_choices': Mantenimiento.ESTADO_REGISTRO_CHOICES,
        'q': q,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_registros': mantenimientos.count(),
    }

    return render(request, 'mantenimiento/historial_producto.html', context)