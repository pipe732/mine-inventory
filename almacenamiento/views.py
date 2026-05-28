from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .forms import EstanteForm, AlmacenForm
from .models import Estante, Almacen
from common.mixins import sesion_requerida
import qrcode
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.http import HttpResponse
from django.conf import settings

def registro_qr_pdf(request):
    # URL de registro — usa tu dominio real en producción
    url_registro = request.build_absolute_uri('/usuario/registro/')

    # Generar el QR en memoria
    qr = qrcode.make(url_registro)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # Crear el PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    ancho, alto = A4

    # Título
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(ancho / 2, alto - 5 * cm, "Registro de Usuarios")

    # Insertar QR en el PDF
    from reportlab.lib.utils import ImageReader
    qr_img = ImageReader(qr_buffer)
    c.drawImage(qr_img, ancho / 2 - 5 * cm, alto / 2 - 3 * cm, width=10 * cm, height=10 * cm)

    # Instrucción debajo del QR
    c.setFont("Helvetica", 12)
    c.drawCentredString(ancho / 2, alto / 2 - 4 * cm, "Escanea para registrarte")

    c.save()
    pdf_buffer.seek(0)

    return HttpResponse(pdf_buffer, content_type='application/pdf',
                        headers={'Content-Disposition': 'inline; filename="registro_qr.pdf"'})


@sesion_requerida
def vista_almacenes(request):
    almacenes = Almacen.objects.all()
    form = AlmacenForm()
    form_editar = None          # ← para devolver errores al modal editar
    show_modal_editar = False   # ← para reabrir el modal editar

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear':
            form = AlmacenForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('almacenes')
            # si hay errores, show_modal=True abre el modal crear

        elif accion == 'editar':
            pk = request.POST.get('almacen_id')
            almacen = get_object_or_404(Almacen, pk=pk)
            form_editar = AlmacenForm(request.POST, instance=almacen)
            if form_editar.is_valid():
                form_editar.save()
                return redirect('almacenes')
            # si hay errores, se devuelve form_editar con mensajes
            show_modal_editar = True

        elif accion == 'eliminar':
            pk = request.POST.get('almacen_id')
            get_object_or_404(Almacen, pk=pk).delete()
            return redirect('almacenes')

    return render(request, 'almacenes.html', {
        'almacenes': almacenes,
        'form': form,
        'form_editar': form_editar,
        'show_modal': bool(form.errors),
        'show_modal_editar': show_modal_editar,
        'total_almacenes': almacenes.count(),
        'total_estantes': Estante.objects.count(),
    })


@sesion_requerida
def vista_estantes(request):
    estantes = Estante.objects.all()
    form = EstanteForm()
    form_editar = None          # ← para devolver errores al modal editar
    show_modal_editar = False

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear':
            form = EstanteForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('estantes')

        elif accion == 'editar':
            pk = request.POST.get('estante_id')
            estante = get_object_or_404(Estante, pk=pk)
            form_editar = EstanteForm(request.POST, instance=estante)
            if form_editar.is_valid():
                form_editar.save()
                return redirect('estantes')
            show_modal_editar = True

        elif accion == 'eliminar':
            pk = request.POST.get('estante_id')
            get_object_or_404(Estante, pk=pk).delete()
            return redirect('estantes')

    return render(request, 'estantes.html', {
        'estantes': estantes,
        'almacenes': Almacen.objects.all(),
        'form': form,
        'form_editar': form_editar,
        'show_modal': bool(form.errors),
        'show_modal_editar': show_modal_editar,
        'total_estantes': estantes.count(),           # ← agregar
        'total_almacenes': Almacen.objects.count(),   # ← agregar
    })


@sesion_requerida
def crear_estante(request):
    return redirect('estantes')

def detalle_almacen(request, pk):
    almacen = get_object_or_404(Almacen, pk=pk)
    estantes = Estante.objects.filter(almacen=almacen)
    return render(request, 'detalle_almacen.html', {
        'almacen': almacen,
        'estantes': estantes,
    })