# mantenimiento/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from .mixins import SesionRequeridaMixin, ContextoMixin
from .models import TipoEstado, Mantenimiento          # ← EstadoHerramienta eliminado
from .forms import TipoEstadoForm, MantenimientoForm
from inventario.models import Producto


# ══════════════════════════════════════════════
# TIPO DE ESTADO
# ══════════════════════════════════════════════

class TipoEstadoListView(SesionRequeridaMixin, ContextoMixin, ListView):
    model               = TipoEstado
    template_name       = 'mantenimiento/tipo_estado_list.html'
    context_object_name = 'estados'
    ordering            = ['nombre']
    titulo              = 'Catálogo de Tipos de Estado'
    subtitulo           = 'Gestión del catálogo de estados de mantenimiento'
    url_accion          = reverse_lazy('mantenimiento:tipo_estado_nuevo')
    label_accion        = 'Nuevo Tipo de Estado'


class TipoEstadoCreateView(SesionRequeridaMixin, ContextoMixin, CreateView):
    model          = TipoEstado
    form_class     = TipoEstadoForm
    template_name  = 'mantenimiento/tipo_estado_form.html'
    success_url    = reverse_lazy('mantenimiento:tipo_estado_lista')
    titulo         = 'Nuevo Tipo de Estado'
    subtitulo      = 'Agrega un nuevo estado al catálogo'
    boton_texto    = 'Guardar Tipo de Estado'
    url_cancelar   = 'mantenimiento:tipo_estado_lista'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Tipo de estado "{form.cleaned_data["nombre"]}" registrado correctamente.'
        )
        return response


class TipoEstadoUpdateView(SesionRequeridaMixin, ContextoMixin, UpdateView):
    model          = TipoEstado
    form_class     = TipoEstadoForm
    template_name  = 'mantenimiento/tipo_estado_form.html'
    success_url    = reverse_lazy('mantenimiento:tipo_estado_lista')
    titulo         = 'Editar Tipo de Estado'
    subtitulo      = 'Modifica los datos del estado seleccionado'
    boton_texto    = 'Guardar Cambios'
    url_cancelar   = 'mantenimiento:tipo_estado_lista'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Tipo de estado "{self.object.nombre}" actualizado correctamente.'
        )
        return response


# ══════════════════════════════════════════════
# MANTENIMIENTO
# ══════════════════════════════════════════════

class MantenimientoListView(SesionRequeridaMixin, ListView):
    model               = Mantenimiento
    template_name       = 'mantenimiento/mantenimiento_lista.html'
    context_object_name = 'registros'

    def get_queryset(self):
        qs = Mantenimiento.objects.select_related(
            'producto', 'tipo_estado', 'responsable'
        ).order_by('-fecha_reporte')

        q      = self.request.GET.get('q', '')
        tipo   = self.request.GET.get('tipo', '')
        estado = self.request.GET.get('estado_registro', '')

        if q:
            qs = qs.filter(
                Q(producto__nombre__icontains=q)       |
                Q(producto__codigo_sku__icontains=q)   |
                Q(descripcion_problema__icontains=q)
            )
        if tipo:
            qs = qs.filter(tipo_mantenimiento=tipo)
        if estado:
            qs = qs.filter(estado_registro=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipo_choices']  = Mantenimiento.TIPO_CHOICES
        ctx['estado_choices']= Mantenimiento.ESTADO_REGISTRO_CHOICES
        ctx['q']             = self.request.GET.get('q', '')
        ctx['tipo_filtro']   = self.request.GET.get('tipo', '')
        ctx['estado_filtro'] = self.request.GET.get('estado_registro', '')
        return ctx


class MantenimientoDetailView(SesionRequeridaMixin, DetailView):
    model               = Mantenimiento
    template_name       = 'mantenimiento/mantenimiento_detalle.html'
    context_object_name = 'm'

    def get_queryset(self):
        return Mantenimiento.objects.select_related(
            'producto', 'tipo_estado', 'responsable', 'creado_por'
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url_cancelar'] = reverse_lazy('mantenimiento:mantenimiento_lista')
        return ctx


#estado actual

class EstadoActualListView(SesionRequeridaMixin, ListView):
    model               = Producto
    template_name       = 'mantenimiento/estado_actual.html'
    context_object_name = 'productos'

    def get_queryset(self):
        qs         = Producto.objects.prefetch_related('mantenimientos').order_by('nombre')
        q          = self.request.GET.get('q', '').strip()
        disponible = self.request.GET.get('disponible', '')

        if q:
            qs = qs.filter(
                Q(nombre__icontains=q)       |
                Q(codigo_sku__icontains=q)   |
                Q(numero_serie__icontains=q) |
                Q(ubicacion__icontains=q)
            )
        if disponible == 'si':
            qs = qs.filter(disponible=True)
        elif disponible == 'no':
            qs = qs.filter(disponible=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q']                    = self.request.GET.get('q', '')
        ctx['disponible_filtro']    = self.request.GET.get('disponible', '')
        # Estos counts usan el queryset completo sin filtros, correcto para los totales globales
        ctx['total_disponibles']    = Producto.objects.filter(disponible=True).count()
        ctx['total_no_disponibles'] = Producto.objects.filter(disponible=False).count()
        return ctx

#historial mantenimientos

class HistorialProductoView(SesionRequeridaMixin, ListView):
    model               = Mantenimiento
    template_name       = 'mantenimiento/historial_producto.html'
    context_object_name = 'mantenimientos'

    def get_queryset(self):
        #mensaje por si falla
        self.producto = get_object_or_404(Producto, pk=self.kwargs['producto_id'])

        qs = Mantenimiento.objects.filter(
            producto=self.producto
        ).select_related(
            'tipo_estado', 'responsable', 'creado_por'
        ).order_by('-fecha_reporte')

        q           = self.request.GET.get('q', '').strip()
        tipo        = self.request.GET.get('tipo', '')
        estado      = self.request.GET.get('estado_registro', '')
        fecha_desde = self.request.GET.get('fecha_desde', '')
        fecha_hasta = self.request.GET.get('fecha_hasta', '')

        if q:
            qs = qs.filter(
                Q(descripcion_problema__icontains=q) |
                Q(acciones_realizadas__icontains=q)
            )
        if tipo:
            qs = qs.filter(tipo_mantenimiento=tipo)
        if estado:
            qs = qs.filter(estado_registro=estado)
        if fecha_desde:
            qs = qs.filter(fecha_reporte__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_reporte__lte=fecha_hasta)

        self._qs_filtrado = qs
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['producto']       = self.producto
        ctx['tipo_choices']   = Mantenimiento.TIPO_CHOICES
        ctx['estado_choices'] = Mantenimiento.ESTADO_REGISTRO_CHOICES
        ctx['q']              = self.request.GET.get('q', '')
        ctx['tipo_filtro']    = self.request.GET.get('tipo', '')
        ctx['estado_filtro']  = self.request.GET.get('estado_registro', '')
        ctx['fecha_desde']    = self.request.GET.get('fecha_desde', '')
        ctx['fecha_hasta']    = self.request.GET.get('fecha_hasta', '')
        ctx['total_registros']= self._qs_filtrado.count()
        return ctx

#api
def login_requerido(view_func):
    """Decorador de sesión para vistas funcionales."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_requerido
def registrar_desde_inventario(request):
    """
    Recibe el POST del modal de mantenimiento lanzado desde inventario.
    - Si el form es válido  → crea el registro y redirige a inventario con mensaje.
    - Si el form es inválido → guarda datos en sesión y redirige de vuelta
      para que inventario reabra el modal con los errores.
    """
    if request.method != 'POST':
        return redirect('inventario:inventario')

    producto_id = request.POST.get('producto_id')
    producto    = get_object_or_404(Producto, pk=producto_id)

    # MantenimientoForm espera 'producto' como HiddenInput.
    # Lo inyectamos en el POST mutable para que el form lo valide.
    post_data            = request.POST.copy()
    post_data['producto'] = producto_id

    form = MantenimientoForm(post_data)

    if form.is_valid():
        mantenimiento = form.save(commit=False)

        # Auditoría: asignar creado_por desde la sesión propia
        doc = request.session.get('usuario_documento')
        if doc:
            try:
                mantenimiento.creado_por = User.objects.get(username=doc)
            except User.DoesNotExist:
                pass

        mantenimiento.save()
        messages.success(
            request,
            f'Mantenimiento registrado para '
            f'[{producto.codigo_sku}] {producto.nombre}.'
        )
        return redirect('inventario:inventario')

    # Form inválido: guardamos en sesión para que inventario reabra el modal
    request.session['mant_form_data']        = post_data.dict()
    request.session['mant_producto_id_error'] = producto_id
    request.session['mant_sku_error']         = producto.codigo_sku
    request.session['mant_nombre_error']      = producto.nombre

    messages.error(request, 'Revisa los errores del formulario de mantenimiento.')
    return redirect('inventario:inventario')