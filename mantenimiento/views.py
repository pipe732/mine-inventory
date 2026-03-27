from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
import openpyxl

from .models import EstadoHerramienta, TipoEstado
from .forms import TipoEstadoForm

#1)Consultar estados de herramienta 
@login_required
def consultar_tipo_estado(request):
    estados = EstadoHerramienta.objects.all()

    busqueda       = request.GET.get('q', '')
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro  = request.GET.get('estado', '')

    if busqueda:
        estados = estados.filter(
            Q(nombre_herramienta__icontains=busqueda) |
            Q(codigo__icontains=busqueda)
        )

    if categoria_filtro:
        estados = estados.filter(categoria=categoria_filtro)

    if estado_filtro:
        estados = estados.filter(estado=estado_filtro)

#Bloque para hacer importaciones a excel
    if 'export_excel' in request.GET:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = (
            'attachment; filename="Reporte_Estados_Herramientas.xlsx"'
        )
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Estados Registrados"
        ws.append(['Nombre Herramienta', 'Estado Sistema', 'Código', 'Descripción', 'Categoría'])

        for obj in estados:
            ws.append([
                obj.nombre_herramienta,
                obj.estado,
                obj.codigo,
                obj.descripcion,       
                obj.get_categoria_display(),
            ])

        wb.save(response)
        return response

    return render(request, 'mantenimiento/consultar_estado.html', { 
        'estados':   estados,
        'busqueda':  busqueda,
    })

#2)Crear un nuevo tipo de estado
@login_required
@permission_required('mantenimiento.add_tipoestado', raise_exception=True)
def tipo_estado_nuevo(request):
    if request.method == 'POST':
        form = TipoEstadoForm(request.POST)
        if form.is_valid():
            tipo_estado = form.save(commit=False)
            tipo_estado.creado_por = request.user
            tipo_estado.save()
            messages.success(
                request,
                f'Tipo de estado "{tipo_estado.nombre}" registrado correctamente.'
            )
            return redirect('mantenimiento:tipo_estado_lista')
    else:
        form = TipoEstadoForm()

    return render(request, 'mantenimiento/tipo_estado_form.html', {'form': form})

#3)Listar los tipos de estado
@login_required
@permission_required('mantenimiento.view_tipoestado', raise_exception=True)
def tipo_estado_lista(request):
    estados = TipoEstado.objects.all().order_by('nombre')
    return render(request, 'mantenimiento/tipo_estado_list.html', {
        'estados': estados,
    })

#4) Editar tipos de estado
@login_required
@permission_required('mantenimiento.change_tipoestado', raise_exception=True)
def tipo_estado_editar(request, pk):
    tipo_estado = get_object_or_404(TipoEstado, pk=pk)

    if request.method == 'POST':
        form = TipoEstadoForm(request.POST, instance=tipo_estado)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Tipo de estado "{tipo_estado.nombre}" actualizado correctamente.'
            )
            return redirect('mantenimiento:tipo_estado_lista')
    else:
        form = TipoEstadoForm(instance=tipo_estado)

    return render(request, 'mantenimiento/editar_tipo_estado.html', {
        'form':         form,
        'title':        'Editar Tipo de Estado',
        'boton_texto':  'Guardar Cambios',
    })

#AQUI VAN LOS MODELOS SIGUIENTES POR EL MOMENTO TENEMOS (4 MODELOS)