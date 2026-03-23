from django.shortcuts import render
from django.http import HttpResponse
from .models import EstadoHerramienta
from django.db.models import Q
import openpyxl # Para generar el Excel

#Importaciones para el segundo modelo
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import TipoEstado
from .forms import TipoEstadoForm

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

class TipoEstadoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = TipoEstado
    form_class = TipoEstadoForm
    template_name = 'mantenimiento/tipo_estado_form.html'
    success_url = reverse_lazy('mantenimiento:consultar_estado')  # ← vuelve a tu lista actual
    success_message = '✅ Tipo de estado "%(nombre)s" registrado correctamente.'
    permission_required = 'mantenimiento.add_tipoestado'   # Django lo crea automáticamente

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)