from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
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
    post_stock = "0"
    post_categoria = ""
    post_cat_nombre = ""
    post_cat_descripcion = ""

    if request.method == "POST":
        accion = request.POST.get("accion", "")

        # ── PRODUCTO: crear ──
        if accion == "crear_producto":
            post_sku = request.POST.get("codigo_sku", "")
            post_nombre = request.POST.get("nombre", "")
            post_descripcion = request.POST.get("descripcion", "")
            post_stock = request.POST.get("stock", "0")
            post_categoria = request.POST.get("categoria", "")

            form = ProductoForm(request.POST)

            if form.is_valid():
                sku = form.cleaned_data.get("codigo_sku", "")

                if Producto.objects.filter(codigo_sku__iexact=sku).exists():
                    error_producto = f'El código / SKU "{sku}" ya está registrado.'
                    form_modal_errors = True
                else:
                    try:
                        p = form.save(commit=False)

                        estante_id = request.POST.get("estante")
                        if estante_id:
                            try:
                                p.estante = Estante.objects.get(pk=estante_id)
                                p.almacen = p.estante.almacen
                            except Estante.DoesNotExist:
                                pass

                        # ✅ usar el stock del formulario
                        p.stock = form.cleaned_data.get("stock", 0)

                        p.save()

                        messages.success(request, f'Herramienta "{p.nombre}" creada correctamente.')
                        return redirect("inventario:inventario")

                    except IntegrityError:
                        error_producto = f'El código / SKU "{sku}" ya está registrado.'
                        form_modal_errors = True

            else:
                if "codigo_sku" in form.errors:
                    error_producto = f'El código / SKU "{post_sku}" ya está registrado.'
                else:
                    error_producto = "Error al guardar."

                form_modal_errors = True

        # ── PRODUCTO: editar ──
        elif accion == "editar_producto":
            pk = request.POST.get("producto_id")
            producto = get_object_or_404(Producto, pk=pk)

            form = ProductoForm(request.POST, instance=producto)

            if form.is_valid():
                sku = form.cleaned_data.get("codigo_sku", "")

                if Producto.objects.filter(codigo_sku__iexact=sku).exclude(pk=pk).exists():
                    messages.error(request, f'El código / SKU "{sku}" ya está en uso.')
                else:
                    try:
                        p = form.save(commit=False)

                        estante_id = request.POST.get("estante")
                        if estante_id:
                            try:
                                p.estante = Estante.objects.get(pk=estante_id)
                                p.almacen = p.estante.almacen
                            except Estante.DoesNotExist:
                                pass

                        p.save()

                        messages.success(request, f'Herramienta "{producto.nombre}" actualizada.')
                        return redirect("inventario:inventario")

                    except IntegrityError:
                        messages.error(request, f'El código / SKU "{sku}" ya está en uso.')

            else:
                messages.error(request, "Error al guardar.")

        # ── PRODUCTO: eliminar ──
        elif accion == "eliminar_producto":
            pk = request.POST.get("producto_id")
            producto = get_object_or_404(Producto, pk=pk)
            nombre = producto.nombre
            producto.delete()
            messages.success(request, f'Herramienta "{nombre}" eliminada.')
            return redirect("inventario:inventario")

        # ── CATEGORÍA: crear ──
        elif accion == "crear_categoria":
            post_cat_nombre = request.POST.get("cat_nombre", "").strip()
            post_cat_descripcion = request.POST.get("cat_descripcion", "").strip()

            if post_cat_nombre:
                if Categoria.objects.filter(nombre__iexact=post_cat_nombre).exists():
                    error_categoria = f'La categoría "{post_cat_nombre}" ya existe.'
                    modal_categoria_errors = True
                else:
                    Categoria.objects.create(
                        nombre=post_cat_nombre,
                        descripcion=post_cat_descripcion or None
                    )
                    messages.success(request, f'Categoría "{post_cat_nombre}" creada.')
                    return redirect("inventario:inventario")
            else:
                error_categoria = "El nombre es obligatorio."
                modal_categoria_errors = True

        # ── CATEGORÍA: editar ──
        elif accion == "editar_categoria":
            pk = request.POST.get("categoria_id")
            categoria = get_object_or_404(Categoria, pk=pk)

            nombre = request.POST.get("cat_nombre", "").strip()
            descripcion = request.POST.get("cat_descripcion", "").strip()

            if nombre:
                if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                    messages.error(request, "Categoría ya existe.")
                else:
                    categoria.nombre = nombre
                    categoria.descripcion = descripcion or None
                    categoria.save()
                    messages.success(request, "Categoría actualizada.")
                    return redirect("inventario:inventario")
            else:
                messages.error(request, "Nombre obligatorio.")

        # ── CATEGORÍA: eliminar ──
        elif accion == "eliminar_categoria":
            pk = request.POST.get("categoria_id")
            categoria = get_object_or_404(Categoria, pk=pk)
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada.')
            return redirect("inventario:inventario")

    # ── GET ──
    productos = Producto.objects.select_related("categoria").all()
    categorias = Categoria.objects.prefetch_related("productos").all()

    if form_filtro.is_valid():
        busqueda = form_filtro.cleaned_data.get("busqueda")
        cat_filtro = form_filtro.cleaned_data.get("categoria")

        if busqueda:
            productos = productos.filter(
                Q(nombre__icontains=busqueda) |
                Q(codigo_sku__icontains=busqueda)
            )

        if cat_filtro:
            productos = productos.filter(categoria=cat_filtro)

    # mantenimiento
    mant_producto_id = request.session.pop('mant_producto_id_error', None)
    mant_sku = request.session.pop('mant_sku_error', '')
    mant_nombre = request.session.pop('mant_nombre_error', '')
    mant_form_saved = request.session.pop('mant_form_data', None)

    if mant_form_saved:
        mant_form = MantenimientoForm(mant_form_saved)
        mant_form.is_valid()
        mant_modal_errors = True
    else:
        mant_form = MantenimientoForm()
        mant_modal_errors = False

    # KPIs
    total_productos = productos.count()
    total_stock = productos.aggregate(s=Sum("stock"))["s"] or 0
    sin_stock = productos.filter(stock=0).count()
    stock_bajo = productos.filter(stock__lte=5).count()

    context = {
        "productos": productos,
        "categorias": categorias,
        "almacenes_lista": Almacen.objects.all(),
        "estantes": Estante.objects.all(),
        "form_filtro": form_filtro,
        "form_modal_errors": form_modal_errors,
        "modal_categoria_errors": modal_categoria_errors,
        "error_producto": error_producto,
        "error_categoria": error_categoria,
        "post_sku": post_sku,
        "post_nombre": post_nombre,
        "post_descripcion": post_descripcion,
        "post_stock": post_stock,
        "post_categoria": post_categoria,
        "post_cat_nombre": post_cat_nombre,
        "post_cat_descripcion": post_cat_descripcion,
        "kpi_total_productos": total_productos,
        "kpi_total_stock": total_stock,
        "kpi_sin_stock": sin_stock,
        "kpi_stock_bajo": stock_bajo,
        "mant_form": mant_form,
        "mant_modal_errors": mant_modal_errors,
        "mant_producto_id_error": mant_producto_id or '',
        "mant_sku_error": mant_sku,
        "mant_nombre_error": mant_nombre,
    }

    return render(request, "inventario.html", context)