from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import EstadoHerramienta, TipoEstado
from .forms import TipoEstadoForm


def login_requerido(view_func):
    """Decorador simple que usa tu sistema de sesiones."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_requerido
def consultar_tipo_estado(request):
    estados = EstadoHerramienta.objects.all()

    busqueda        = request.GET.get('q', '')
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro   = request.GET.get('estado', '')

    if busqueda:
        estados = estados.filter(
            Q(nombre_herramienta__icontains=busqueda) |
            Q(codigo__icontains=busqueda)
        )
    if categoria_filtro:
        estados = estados.filter(categoria=categoria_filtro)
    if estado_filtro:
        estados = estados.filter(estado=estado_filtro)

    return render(request, 'consultar_estado.html', {
        'estados': estados,
        'busqueda': busqueda,
    })


@login_requerido
def tipo_estado_lista(request):
    estados = TipoEstado.objects.all().order_by('nombre')
    return render(request, 'tipo_estado_list.html', {'estados': estados})


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

    return render(request, 'tipo_estado_form.html', {'form': form})


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

    return render(request, 'editar_tipo_estado.html', {
        'form': form,
        'title': 'Editar Tipo de Estado',
        'boton_texto': 'Guardar Cambios',
    })