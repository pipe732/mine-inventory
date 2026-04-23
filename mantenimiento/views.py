# mantenimiento/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from common.mixins import SesionRequeridaMixin, ContextoMixin
from .models import TipoEstado, Mantenimiento
from .forms import TipoEstadoForm, MantenimientoForm, MantenimientoUpdateForm
from inventario.models import Producto


ROLES_ADMIN_EDICION = {'supervisor', 'administrador', 'admin'}
ESTADOS_EDITABLES = {'abierto', 'en_proceso', 'pendiente', 'cerrado_parcial', 'cerrado'}


def _get_usuario_sesion(request):
    documento = request.session.get('usuario_documento')
    if not documento:
        return None
    try:
        return User.objects.get(username=documento)
    except User.DoesNotExist:
        return None


def _get_rol_sesion(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return 'admin'
    return (request.session.get('usuario_rol') or '').strip().lower()


def _es_rol_admin(rol):
    return rol in ROLES_ADMIN_EDICION or 'admin' in rol or 'supervisor' in rol or 'administrador' in rol


def _es_rol_tecnico(rol):
    return 'tecnico' in rol


def _puede_editar_mantenimiento(request, mantenimiento):
    if request.user.is_authenticated and request.user.is_superuser:
        return True

    rol = _get_rol_sesion(request)
    documento = request.session.get('usuario_documento')

    if mantenimiento.estado_registro not in ESTADOS_EDITABLES and not _es_rol_admin(rol):
        return False

    if _es_rol_admin(rol):
        return True

    if _es_rol_tecnico(rol):
        if not mantenimiento.responsable_id:
            return False
        return mantenimiento.responsable.username == documento

    return False


def _es_cambio_significativo(cambios):
    campos_clave = {'estado_registro', 'costo_real', 'costo_estimado', 'responsable'}
    return any(campo in cambios for campo in campos_clave)


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
        ctx['editable_ids']  = {
            m.pk for m in ctx['registros'] if _puede_editar_mantenimiento(self.request, m)
        }
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
            'producto', 'tipo_estado', 'responsable', 'creado_por', 'actualizado_por'
        ).prefetch_related('cambios_auditoria__editado_por')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url_cancelar'] = reverse_lazy('mantenimiento:mantenimiento_lista')
        ctx['puede_editar'] = _puede_editar_mantenimiento(self.request, self.object)
        ctx['cambios_auditoria'] = self.object.cambios_auditoria.all()[:20]
        return ctx


class MantenimientoUpdateView(SesionRequeridaMixin, ContextoMixin, UpdateView):
    model = Mantenimiento
    form_class = MantenimientoUpdateForm
    template_name = 'mantenimiento/mantenimiento_form.html'
    titulo = 'Editar Mantenimiento'
    subtitulo = 'Actualiza la orden sin perder trazabilidad'
    boton_texto = 'Guardar cambios'
    url_cancelar = 'mantenimiento:mantenimiento_lista'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not _puede_editar_mantenimiento(request, self.object):
            messages.error(
                request,
                'No tienes permisos para editar este registro o su estado no permite edición.'
            )
            return HttpResponseForbidden('Acceso denegado para editar este mantenimiento.')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['rol_usuario'] = _get_rol_sesion(self.request)
        kwargs['usuario_documento'] = self.request.session.get('usuario_documento')
        return kwargs

    def form_valid(self, form):
        cambios = form.get_changed_fields()
        motivo = form.cleaned_data.get('motivo_edicion')
        detalle = form.cleaned_data.get('detalle_motivo', '')

        mantenimiento = form.save(commit=False)
        mantenimiento.actualizado_por = _get_usuario_sesion(self.request)
        mantenimiento.save()

        mantenimiento.registrar_cambio(
            editado_por=mantenimiento.actualizado_por,
            motivo_edicion=motivo,
            cambios=cambios,
            detalle_motivo=detalle,
        )

        messages.success(self.request, 'La orden de mantenimiento se actualizó correctamente.')
        if _es_cambio_significativo(cambios):
            messages.info(
                self.request,
                'Se registró un cambio significativo; puedes notificar al supervisor desde el historial.'
            )
        return redirect('mantenimiento:mantenimiento_detalle', pk=mantenimiento.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mantenimiento'] = self.object
        ctx['solo_campos_tecnico'] = _es_rol_tecnico(_get_rol_sesion(self.request))
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
        ctx['editable_ids']   = {
            m.pk for m in ctx['mantenimientos'] if _puede_editar_mantenimiento(self.request, m)
        }
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

    form = MantenimientoForm(post_data, request.FILES)

    if form.is_valid():
        mantenimiento = form.save(commit=False)

        # Auditoría: asignar creado_por desde la sesión propia
        doc = request.session.get('usuario_documento')
        if doc:
            try:
                usuario = User.objects.get(username=doc)
                mantenimiento.creado_por = usuario
                mantenimiento.actualizado_por = usuario
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