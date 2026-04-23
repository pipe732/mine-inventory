from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.db import IntegrityError

from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm, FiltroInventarioForm
from mantenimiento.forms import MantenimientoForm


def inventario(request):
    form_filtro = FiltroInventarioForm(request.GET or None)

    # Variables de control de errores
    form_modal_errors = False
    modal_categoria_errors = False
    error_producto = ""
    error_categoria = ""

    # Valores para repoblar los campos tras un error
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
                    error_producto = f'El código / SKU "{sku}" ya está registrado. Usa uno diferente.'
                    form_modal_errors = True
                else:
                    try:
                        p = form.save(commit=False)
                        p.stock = 1
                        p.save()
                        messages.success(request, f'Herramienta "{p.nombre}" creada correctamente.')
                        return redirect("inventario:inventario")
                    except IntegrityError:
                        error_producto = f'El código / SKU "{sku}" ya está registrado. Usa uno diferente.'
                        form_modal_errors = True
            else:
                if "codigo_sku" in form.errors:
                    error_producto = f'El código / SKU "{post_sku}" ya está registrado. Usa uno diferente.'
                else:
                    error_producto = "Error al guardar. Revisa los campos."
                form_modal_errors = True

        # ── PRODUCTO: editar ──
        elif accion == "editar_producto":
            pk = request.POST.get("producto_id")
            producto = get_object_or_404(Producto, pk=pk)
            form = ProductoForm(request.POST, instance=producto)
            if form.is_valid():
                sku = form.cleaned_data.get("codigo_sku", "")
                if Producto.objects.filter(codigo_sku__iexact=sku).exclude(pk=pk).exists():
                    messages.error(request, f'El código / SKU "{sku}" ya está en uso por otra herramienta.')
                else:
                    try:
                        form.save()
                        messages.success(request, f'Herramienta "{producto.nombre}" actualizada correctamente.')
                        return redirect("inventario:inventario")
                    except IntegrityError:
                        messages.error(request, f'El código / SKU "{sku}" ya está en uso por otra herramienta.')
            else:
                if "codigo_sku" in form.errors:
                    sku = request.POST.get("codigo_sku", "")
                    messages.error(request, f'El código / SKU "{sku}" ya está en uso por otra herramienta.')
                else:
                    messages.error(request, "Error al guardar. Revisa los campos.")

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
                    error_categoria = f'La categoría "{post_cat_nombre}" ya existe. Elige un nombre diferente.'
                    modal_categoria_errors = True
                else:
                    try:
                        Categoria.objects.create(
                            nombre=post_cat_nombre,
                            descripcion=post_cat_descripcion or None
                        )
                        messages.success(request, f'Categoría "{post_cat_nombre}" creada correctamente.')
                        return redirect("inventario:inventario")
                    except IntegrityError:
                        error_categoria = f'La categoría "{post_cat_nombre}" ya existe. Elige un nombre diferente.'
                        modal_categoria_errors = True
            else:
                error_categoria = "El nombre de la categoría es obligatorio."
                modal_categoria_errors = True

        # ── CATEGORÍA: editar ──
        elif accion == "editar_categoria":
            pk = request.POST.get("categoria_id")
            categoria = get_object_or_404(Categoria, pk=pk)
            nombre = request.POST.get("cat_nombre", "").strip()
            descripcion = request.POST.get("cat_descripcion", "").strip()

            if nombre:
                if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                    messages.error(request, f'Ya existe una categoría llamada "{nombre}". Elige un nombre diferente.')
                else:
                    try:
                        categoria.nombre = nombre
                        categoria.descripcion = descripcion or None
                        categoria.save()
                        messages.success(request, f'Categoría "{nombre}" actualizada.')
                        return redirect("inventario:inventario")
                    except IntegrityError:
                        messages.error(request, f'Ya existe una categoría llamada "{nombre}". Elige un nombre diferente.')
            else:
                messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect("inventario:inventario")

        # ── CATEGORÍA: eliminar ──
        elif accion == "eliminar_categoria":
            pk = request.POST.get("categoria_id")
            categoria = get_object_or_404(Categoria, pk=pk)
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada.')
            return redirect("inventario:inventario")

    # ── GET: lista con filtros ──
    productos  = Producto.objects.select_related("categoria").all()
    categorias = Categoria.objects.prefetch_related("productos").all()
    if form_filtro.is_valid():
        busqueda = form_filtro.cleaned_data.get("busqueda")
        cat_filtro = form_filtro.cleaned_data.get("categoria")
        if busqueda:
            productos = productos.filter(
                Q(nombre__icontains=busqueda) | Q(codigo_sku__icontains=busqueda)
            )
        if cat_filtro:
            productos = productos.filter(categoria=cat_filtro)

    #modal de mantenimiento
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

    # ── Ordenamiento dinámico ──
    orden = request.GET.get("orden", "nombre")
    direccion = request.GET.get("dir", "asc")
    campos_validos = {"nombre", "codigo_sku", "stock", "categoria__nombre"}
    if orden not in campos_validos:
        orden = "nombre"
    orden_db = f"-{orden}" if direccion == "desc" else orden
    productos = productos.order_by(orden_db)

    # ── KPIs ──
    total_productos = productos.count()
    total_stock     = productos.aggregate(s=Sum("stock"))["s"] or 0
    sin_stock       = productos.filter(stock=0).count()
    stock_bajo      = productos.filter(stock__gt=0, stock__lte=5).count()

    # Alertas de stock bajo
    alertas_stock = Producto.objects.filter(stock__lte=5).order_by("stock").values_list("nombre", "stock")[:5]

    context = {
        "productos":              productos,
        "categorias":             categorias,
        "form_filtro":            form_filtro,
        "form_modal_errors":      form_modal_errors,
        "modal_categoria_errors": modal_categoria_errors,
        "error_producto":         error_producto,
        "error_categoria":        error_categoria,
        "post_sku":               post_sku,
        "post_nombre":            post_nombre,
        "post_descripcion":       post_descripcion,
        "post_stock":             post_stock,
        "post_categoria":         post_categoria,
        "post_cat_nombre":        post_cat_nombre,
        "post_cat_descripcion":   post_cat_descripcion,
        "total":                  total_productos,
        # KPIs
        "kpi_total_productos":    total_productos,
        "kpi_total_stock":        total_stock,
        "kpi_sin_stock":          sin_stock,
        "kpi_stock_bajo":         stock_bajo,
        # Ordenamiento activo
        "orden_activo":           orden,
        "dir_activo":             direccion,
        # Alertas de stock
        "alertas_stock":          alertas_stock,
        "hay_alertas":            bool(alertas_stock),

        # Variables para mantenimiento
        "mant_form":              mant_form,
        "mant_modal_errors":      mant_modal_errors,
        "mant_producto_id_error": mant_producto_id or '',
        "mant_sku_error":         mant_sku,
        "mant_nombre_error":      mant_nombre,
    }

    return render(request, "inventario.html", context)