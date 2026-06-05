from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db import IntegrityError
from almacenamiento.models import Almacen, Estante
from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm, FiltroInventarioForm
from mantenimiento.forms import MantenimientoForm
from common.mixins import sesion_requerida    

@sesion_requerida
def inventario(request):
    form_filtro = FiltroInventarioForm(request.GET or None)

    # Variables de control de errores
    form_modal_errors = False
    modal_categoria_errors = False
    error_producto = ""
    error_categoria = ""

    # Valores para repoblar
    post_sku = ""
    post_nombre = ""
    post_descripcion = ""
    post_stock = "1"
    post_categoria = ""
    post_cat_nombre = ""
    post_cat_descripcion = ""

    if request.method == "POST":
        accion = request.POST.get("accion", "")

        # ── PRODUCTO: crear ──
        if accion == "crear_producto":
            post_sku = request.POST.get("codigo_sku", "").strip()
            post_nombre = request.POST.get("nombre", "").strip()
            post_descripcion = request.POST.get("descripcion", "").strip()
            post_categoria = request.POST.get("categoria", "")
            post_stock = request.POST.get("stock", "1").strip() or "1"

            try:
                stock_value = int(post_stock)
                if stock_value < 0:
                    raise ValueError

                cat_instancia = None
                if post_categoria:
                    cat_instancia = Categoria.objects.get(pk=post_categoria)

                Producto.objects.create(
                    codigo_sku=post_sku,
                    nombre=post_nombre,
                    descripcion=post_descripcion,
                    stock=stock_value,
                    categoria=cat_instancia,
                    disponible=True
                )
                messages.success(request, f"Herramienta '{post_nombre}' registrada con éxito.")
                return redirect("inventario:inventario")

            except IntegrityError:
                error_producto = "El Código SKU ya se encuentra registrado. Ingrese uno diferente."
                form_modal_errors = True
            except ValueError:
                error_producto = "El stock debe ser un número entero mayor o igual a 0."
                form_modal_errors = True
            except Exception as e:
                error_producto = f"Error al guardar: {str(e)}"
                form_modal_errors = True

        # ── PRODUCTO: editar ──
        elif accion == "editar_producto":
            producto_id = request.POST.get("producto_id")
            prod = get_object_or_404(Producto, pk=producto_id)
            
            prod.codigo_sku = request.POST.get("codigo_sku", "").strip()
            prod.nombre = request.POST.get("nombre", "").strip()
            prod.descripcion = request.POST.get("descripcion", "").strip()
            
            try:
                stock_value = int(request.POST.get("stock", prod.stock))
                if stock_value < 0:
                    raise ValueError
                prod.stock = stock_value
            except ValueError:
                messages.error(request, "El stock debe ser un número entero mayor o igual a 0.")
                return redirect("inventario:inventario")

            cat_id = request.POST.get("categoria")
            if cat_id:
                prod.categoria = Categoria.objects.get(pk=cat_id)
            else:
                prod.categoria = None
                
            try:
                prod.save()
                messages.success(request, f"Información de '{prod.nombre}' actualizada.")
                return redirect("inventario:inventario")
            except IntegrityError:
                messages.error(request, "Error: El SKU ingresado ya pertenece a otra herramienta.")
                return redirect("inventario:inventario")

        # ── PRODUCTO: eliminar ──
        elif accion == "eliminar_producto":
            producto_id = request.POST.get("producto_id")
            prod = get_object_or_404(Producto, pk=producto_id)
            nombre_prod = prod.nombre
            prod.delete()
            messages.success(request, f"Herramienta '{nombre_prod}' eliminada permanentemente.")
            return redirect("inventario:inventario")

        # ── CATEGORIA: crear rápida ──
       # ── CATEGORIA: crear rápida ──
        elif accion == "crear_categoria":
            post_cat_nombre = request.POST.get("cat_nombre", "").strip()
            post_cat_descripcion = request.POST.get("cat_descripcion", "").strip()

            # Conservamos los datos del producto por si se estaba llenando el modal de herramientas
            post_sku = request.POST.get("codigo_sku", "").strip()
            post_nombre = request.POST.get("nombre", "").strip()
            post_descripcion = request.POST.get("descripcion", "").strip()
            post_stock = request.POST.get("stock", "1").strip() or "1"

            try:
                nueva_cat = Categoria.objects.create(nombre=post_cat_nombre, descripcion=post_cat_descripcion)
                messages.success(request, f"Categoría '{post_cat_nombre}' creada correctamente.")
                
                # Si el usuario vino desde el modal de producto, guardamos su ID para preseleccionarla
                post_categoria = str(nueva_cat.pk)
                
                # Si venía del modal de producto, forzamos a que el modal se vuelva a abrir automáticamente
                if post_sku or post_nombre:
                    request.session['abrir_modal_producto'] = True

                return redirect("inventario:inventario")
                
            except IntegrityError:
                error_categoria = "Esta categoría ya existe."
                modal_categoria_errors = True
                form_modal_errors = True  # Mantiene el flujo para regresar al modal principal

    # Consultar herramientas y categorías para la vista
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()

    from usuario.models import Usuario
    usuarios_sistema = Usuario.objects.all().order_by('nombre_completo')

    # Manejo de errores de formularios externos (Mantenimiento)
    mant_form_data = request.session.pop('mant_form_data', None)
    mant_producto_id_error = request.session.pop('mant_producto_id_error', '')
    mant_sku_error = request.session.pop('mant_sku_error', '')
    mant_nombre_error = request.session.pop('mant_nombre_error', '')

    if mant_form_data:
        mant_form = MantenimientoForm(mant_form_data)
        mant_modal_errors = True
    else:
        mant_form = MantenimientoForm()
        mant_modal_errors = False

  # KPIs adaptados a la lógica unitaria
    total_productos = productos.count()
    total_stock = productos.aggregate(s=Sum("stock"))["s"] or 0
    sin_stock = productos.filter(stock=0).count()
    stock_bajo = productos.filter(stock__lte=5, stock__gt=0).count()
    
    # ── CONTROL DE REAPERTURA: Validación de categoría rápida ──
    # Si la sesión tiene la bandera, forzamos a True para que el script del HTML abra el modal de herramientas
    if request.session.pop('abrir_modal_producto', False):
        form_modal_errors = True

    context = {
        "productos": productos,
        "categorias": categorias,
        "total": total_productos,
        "form_filtro": form_filtro,
        "form_modal_errors": form_modal_errors,
        "modal_categoria_errors": modal_categoria_errors,
        "mant_modal_errors": mant_modal_errors,
        "error_producto": error_producto,
        "error_categoria": error_categoria,
        "post_sku": post_sku,
        "post_nombre": post_nombre,
        "post_descripcion": post_descripcion,
        "post_stock": post_stock,
        "post_categoria": post_categoria,
        "post_cat_nombre": post_cat_nombre,
        "post_cat_descripcion": post_cat_descripcion,
        "mant_form": mant_form,
        "mant_producto_id_error": mant_producto_id_error,
        "mant_sku_error": mant_sku_error,
        "mant_nombre_error": mant_nombre_error,
        "usuarios_sistema": usuarios_sistema,
        "kpi_total_productos": total_productos,
        "kpi_total_stock": total_stock,
        "kpi_sin_stock": sin_stock,
        "kpi_stock_bajo": stock_bajo,
    }

    return render(request, "inventario.html", context)