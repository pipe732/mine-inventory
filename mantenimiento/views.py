# mantenimiento/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from .mixins import SesionRequeridaMixin, ContextoMixin
from .models import EstadoHerramienta, TipoEstado, Mantenimiento
from .forms import TipoEstadoForm, MantenimientoForm
from inventario.models import Producto


# ══════════════════════════════════════════════
# TIPO DE ESTADO
# ══════════════════════════════════════════════

class TipoEstadoListView(SesionRequeridaMixin, ContextoMixin, ListView):
    model                = TipoEstado
    template_name        = 'mantenimiento/tipo_estado_list.html'
    context_object_name  = 'estados'
    ordering             = ['nombre']
    titulo               = 'Catálogo de Tipos de Estado'
    subtitulo            = 'Gestión del catálogo de estados de mantenimiento'
    url_accion           = reverse_lazy('mantenimiento:tipo_estado_nuevo')
    label_accion         = 'Nuevo Tipo de Estado'


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
                Q(producto__nombre__icontains=q) |
                Q(producto__codigo_sku__icontains=q) |
                Q(descripcion_problema__icontains=q)
            )
        if tipo:
            qs = qs.filter(tipo_mantenimiento=tipo)
        if estado:
            qs = qs.filter(estado_registro=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipo_choices']   = Mantenimiento.TIPO_CHOICES
        ctx['estado_choices'] = Mantenimiento.ESTADO_REGISTRO_CHOICES
        ctx['q']              = self.request.GET.get('q', '')
        ctx['tipo_filtro']    = self.request.GET.get('tipo', '')
        ctx['estado_filtro']  = self.request.GET.get('estado_registro', '')
        return ctx


class MantenimientoCreateView(SesionRequeridaMixin, ContextoMixin, CreateView):
    model          = Mantenimiento
    form_class     = MantenimientoForm
    template_name  = 'mantenimiento/mantenimiento_form.html'
    success_url    = reverse_lazy('mantenimiento:mantenimiento_lista')
    titulo         = 'Nuevo Mantenimiento'
    subtitulo      = 'Registra un mantenimiento correctivo o preventivo'
    boton_texto    = 'Registrar Mantenimiento'
    url_cancelar   = 'mantenimiento:mantenimiento_lista'

    def get_initial(self):
        initial = super().get_initial()
        if producto_pk := self.request.GET.get('producto'):
            initial['producto'] = producto_pk
        return initial

    def form_valid(self, form):
        mantenimiento = form.save(commit=False)

        doc = self.request.session.get('usuario_documento')
        if doc:
            try:
                mantenimiento.creado_por = User.objects.get(username=doc)
            except User.DoesNotExist:
                pass

        mantenimiento.save()
        messages.success(
            self.request,
            f'Mantenimiento registrado para '
            f'[{mantenimiento.producto.codigo_sku}] {mantenimiento.producto.nombre}.'
        )
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Revisa los errores del formulario.')
        return super().form_invalid(form)


class MantenimientoUpdateView(SesionRequeridaMixin, ContextoMixin, UpdateView):
    model          = Mantenimiento
    form_class     = MantenimientoForm
    template_name  = 'mantenimiento/mantenimiento_form.html'
    success_url    = reverse_lazy('mantenimiento:mantenimiento_lista')
    titulo         = 'Editar Mantenimiento'
    subtitulo      = 'Modifica los datos del registro de mantenimiento'
    boton_texto    = 'Guardar Cambios'
    url_cancelar   = 'mantenimiento:mantenimiento_lista'

    def form_valid(self, form):
        response = super().form_valid(form)
        m = self.object
        messages.success(
            self.request,
            f'Mantenimiento de [{m.producto.codigo_sku}] '
            f'{m.producto.nombre} actualizado correctamente.'
        )
        return response


class MantenimientoDetailView(SesionRequeridaMixin, DetailView):
    model               = Mantenimiento
    template_name       = 'mantenimiento/mantenimiento_detalle.html'
    context_object_name = 'm'

    def get_queryset(self):
        return Mantenimiento.objects.select_related(
            'producto', 'tipo_estado', 'responsable', 'creado_por'
        )


# ══════════════════════════════════════════════
# ESTADO ACTUAL
# ══════════════════════════════════════════════

class EstadoActualListView(SesionRequeridaMixin, ListView):
    model               = Producto
    template_name       = 'mantenimiento/estado_actual.html'
    context_object_name = 'productos'

    def get_queryset(self):
        qs          = Producto.objects.prefetch_related('mantenimientos').order_by('nombre')
        q           = self.request.GET.get('q', '').strip()
        disponible  = self.request.GET.get('disponible', '')

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
        ctx['q']                   = self.request.GET.get('q', '')
        ctx['disponible_filtro']   = self.request.GET.get('disponible', '')
        ctx['total_disponibles']   = Producto.objects.filter(disponible=True).count()
        ctx['total_no_disponibles']= Producto.objects.filter(disponible=False).count()
        ctx['url_accion']          = reverse_lazy('mantenimiento:mantenimiento_nuevo')
        ctx['label_accion']        = 'Nuevo Mantenimiento'
        return ctx


# ══════════════════════════════════════════════
# HISTORIAL POR PRODUCTO
# ══════════════════════════════════════════════

class HistorialProductoView(SesionRequeridaMixin, ListView):
    model               = Mantenimiento
    template_name       = 'mantenimiento/historial_producto.html'
    context_object_name = 'mantenimientos'

    def get_queryset(self):
        self.producto = get_object_or_404(Producto, pk=self.kwargs['producto_id'])
        qs = Mantenimiento.objects.filter(
            producto=self.producto
        ).select_related(
            'tipo_estado', 'responsable', 'creado_por'
        ).order_by('-fecha_reporte')

        q           = self.request.GET.get('q', '').strip()
        tipo        = self.request.GET.get('tipo', '')
        estado      = self.request.GET.get('estado_registro', '')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')

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
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['producto']      = self.producto
        ctx['tipo_choices']  = Mantenimiento.TIPO_CHOICES
        ctx['estado_choices']= Mantenimiento.ESTADO_REGISTRO_CHOICES
        ctx['q']             = self.request.GET.get('q', '')
        ctx['tipo_filtro']   = self.request.GET.get('tipo', '')
        ctx['estado_filtro'] = self.request.GET.get('estado_registro', '')
        ctx['fecha_desde']   = self.request.GET.get('fecha_desde', '')
        ctx['fecha_hasta']   = self.request.GET.get('fecha_hasta', '')
        ctx['total_registros']= self.object_list.count()
        ctx['url_accion']    = (
            str(reverse_lazy('mantenimiento:mantenimiento_nuevo'))
            + f'?producto={self.producto.pk}'
        )
        ctx['label_accion']  = 'Nuevo Mantenimiento'
        return ctx


# ══════════════════════════════════════════════
# API AJAX — se queda como FBV, no necesita CBV
# ══════════════════════════════════════════════

def login_requerido(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_requerido
def api_buscar_producto(request):
    q          = request.GET.get('q', '').strip()
    resultados = []

    if len(q) >= 2:
        productos = Producto.objects.filter(
            Q(nombre__icontains=q)        |
            Q(codigo_sku__icontains=q)    |
            Q(numero_serie__icontains=q)
        )[:10]

        for p in productos:
            resultados.append({
                'id'        : p.pk,
                'texto'     : f"[{p.codigo_sku}] {p.nombre}",
                'codigo_sku': p.codigo_sku,
                'nombre'    : p.nombre,
                'ubicacion' : p.ubicacion or '—',
                'disponible': p.disponible,
            })

    return JsonResponse({'resultados': resultados})