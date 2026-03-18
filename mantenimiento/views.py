from django.shortcuts import render
from django.http import HttpResponse
from .models import EstadoHerramienta
from django.db.models import Q
import openpyxl # Para generar el Excel

def consultar_tipo_estado(request):
    # 1. Obtener registros base
    estados = EstadoHerramienta.objects.all()

    busqueda = request.GET.get('q') # Por palabra clave (nombre, código)
    categoria_filtro = request.GET.get('categoria')
    estado_filtro = request.GET.get('estado')

    if busqueda:
        #Busqueda por filtros
        estados = estados.filter(
            Q(nombre_herramienta__icontains=busqueda) | 
            Q(codigo__icontains=busqueda)
        )
    
    if categoria_filtro:
        estados = estados.filter(categoria=categoria_filtro)
    
    if estado_filtro:
        estados = estados.filter(estado=estado_filtro)

    #Exportamos a excel con la libreria instalada
    if 'export_excel' in request.GET:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Reporte_Estados_Herramientas.xlsx"'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Estados Registrados"

        #tablas de excel
        columns = ['Nombre Herramienta', 'Estado Sistema', 'Código', 'Descripción', 'Categoría']
        ws.append(columns)

        for obj in estados:
            ws.append([obj.nombre_herramienta, obj.estado, obj.codigo, obj.description, obj.get_categoria_display()])

        wb.save(response)
        return response

    # Enviamos datos a consultar_estado
    return render(request, 'mantenimiento/consultar_estado.html', {
        'estados': estados,
        'busqueda': busqueda,
    })