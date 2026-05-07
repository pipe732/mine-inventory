#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo.
Genera al menos 10 registros por cada tabla y crea el usuario admin especificado.
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Importar modelos
from usuario.models import Usuario
from almacenamiento.models import Almacen, Estante
from inventario.models import Categoria, Producto
from mantenimiento.models import TipoEstado, Mantenimiento
from prestamo.models import Prestamo, ItemPrestamo
from devoluciones.models import Devolucion
from reportes.models import ReporteHistorial


def crear_usuarios():
    """Crear usuario admin y 10 usuarios de ejemplo."""
    print("\n" + "="*60)
    print("CREANDO USUARIOS")
    print("="*60)
    
    # Crear usuario admin
    admin_doc = '0000000000'
    admin, admin_created = Usuario.objects.get_or_create(
        numero_documento=admin_doc,
        defaults={
            'tipo_documento': 'CC',
            'nombre_completo': 'admin',
            'correo': 'a@b.com',
            'rol': 'Administrador',
            'password': make_password('@dmin123'),
            'telefono': '3000000000'
        }
    )
    if admin_created:
        print(f"✓ Admin creado: {admin_doc} | a@b.com")
    else:
        print(f"→ Admin ya existe: {admin_doc}")
    
    # Crear 10 usuarios normales
    usuarios = []
    for i in range(1, 11):
        doc = f'1000000{i:03d}'
        usuario, created = Usuario.objects.get_or_create(
            numero_documento=doc,
            defaults={
                'tipo_documento': 'CC',
                'nombre_completo': f'Usuario Prueba {i}',
                'correo': f'usuario{i}@ejemplo.com',
                'rol': 'Usuario',
                'password': make_password('Contra123*'),
                'telefono': f'310000{i:04d}'
            }
        )
        usuarios.append(usuario)
        if created:
            print(f"✓ Usuario {i} creado: {doc}")
        else:
            print(f"→ Usuario {i} ya existe: {doc}")
    
    return usuarios


def crear_categorias():
    """Crear 10 categorías de productos."""
    print("\n" + "="*60)
    print("CREANDO CATEGORÍAS")
    print("="*60)
    
    nombres_categorias = [
        'Herramientas Manuales',
        'Herramientas Eléctricas',
        'Equipos de Seguridad',
        'Equipos de Medición',
        'Tuberías y Accesorios',
        'Suministros de Construcción',
        'Equipos de Laboratorio',
        'Herramientas de Precisión',
        'Equipos de Protección',
        'Materiales Diversos'
    ]
    
    categorias = []
    for nombre in nombres_categorias:
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Categoría: {nombre}'}
        )
        categorias.append(cat)
        if created:
            print(f"✓ Categoría creada: {nombre}")
        else:
            print(f"→ Categoría ya existe: {nombre}")
    
    return categorias


def crear_productos(categorias):
    """Crear 10+ productos."""
    print("\n" + "="*60)
    print("CREANDO PRODUCTOS")
    print("="*60)
    
    productos_datos = [
        ('MARTILLO-001', 'Martillo de Goma 32 oz', 'Martillo para trabajos generales', 25, 'Herramientas Manuales'),
        ('DESTORNILLADOR-001', 'Set Destornilladores 12 pcs', 'Set completo de destornilladores', 15, 'Herramientas Manuales'),
        ('TALADRO-001', 'Taladro Inalámbrico 20V', 'Taladro compacto y versátil', 8, 'Herramientas Eléctricas'),
        ('CASCO-001', 'Casco de Seguridad Amarillo', 'Casco ANSI Z89.1', 30, 'Equipos de Seguridad'),
        ('MULTIMETRO-001', 'Multímetro Digital 600V', 'Medidor digital profesional', 5, 'Equipos de Medición'),
        ('TUBO-001', 'Tubo PVC 1 Pulgada 3m', 'Tubo de PVC para agua', 50, 'Tuberías y Accesorios'),
        ('CEMENTO-001', 'Cemento Portland 50 kg', 'Cemento gris estándar', 100, 'Suministros de Construcción'),
        ('MICROSCOPIO-001', 'Microscopio Digital USB', 'Microscopio de laboratorio', 3, 'Equipos de Laboratorio'),
        ('CALIBRADOR-001', 'Calibrador Digital 0-150mm', 'Precisión de 0.01mm', 12, 'Herramientas de Precisión'),
        ('GUANTES-001', 'Guantes de Nitrilo Azules', 'Caja de 100 guantes', 200, 'Equipos de Protección'),
        ('LLAVE-001', 'Juego Llaves Inglesas 8-32mm', 'Set de 8 llaves ajustables', 6, 'Herramientas Manuales'),
        ('SIERRA-001', 'Sierra Circular 7.25 Pulgadas', 'Sierra profesional para corte', 4, 'Herramientas Eléctricas'),
    ]
    
    # Mapear nombres de categorías a objetos
    cat_map = {cat.nombre: cat for cat in categorias}
    
    productos = []
    for sku, nombre, desc, stock, cat_nombre in productos_datos:
        cat = cat_map.get(cat_nombre, categorias[0])
        prod, created = Producto.objects.get_or_create(
            codigo_sku=sku,
            defaults={
                'nombre': nombre,
                'descripcion': desc,
                'stock': stock,
                'categoria': cat,
                'numero_serie': f'SN-{sku}',
                'disponible': True,
                'ubicacion': 'Almacén Principal'
            }
        )
        productos.append(prod)
        if created:
            print(f"✓ Producto creado: {sku} - {nombre} (Stock: {stock})")
        else:
            print(f"→ Producto ya existe: {sku}")
    
    return productos


def crear_almacenes():
    """Crear 10 almacenes."""
    print("\n" + "="*60)
    print("CREANDO ALMACENES")
    print("="*60)
    
    almacenes = []
    for i in range(1, 11):
        almacen, created = Almacen.objects.get_or_create(
            nombre=f'Almacén {i}',
            defaults={
                'detalles': f'Almacén de almacenamiento número {i}',
                'capacidad': random.randint(500, 2000)
            }
        )
        almacenes.append(almacen)
        if created:
            print(f"✓ Almacén {i} creado - Capacidad: {almacen.capacidad}")
        else:
            print(f"→ Almacén {i} ya existe")
    
    return almacenes


def crear_estantes(almacenes):
    """Crear 10 estantes por almacén (mínimo 10 totales)."""
    print("\n" + "="*60)
    print("CREANDO ESTANTES")
    print("="*60)
    
    estantes = []
    # Crear al menos 10 estantes usando algunos almacenes
    contador = 1
    for almacen in almacenes[:2]:  # Usar primeros 2 almacenes
        for i in range(1, 6):  # 5 estantes por almacén = 10 total
            estante, created = Estante.objects.get_or_create(
                codigo=f'EST-{almacen.id}-{i:02d}',
                defaults={
                    'almacen': almacen,
                    'detalles': f'Estante {i} del {almacen.nombre}',
                    'capacidad': random.randint(50, 200)
                }
            )
            estantes.append(estante)
            if created:
                print(f"✓ Estante {contador} creado: EST-{almacen.id}-{i:02d}")
                contador += 1
            else:
                print(f"→ Estante EST-{almacen.id}-{i:02d} ya existe")
    
    return estantes


def crear_tipos_estado():
    """Crear 10 tipos de estado de mantenimiento."""
    print("\n" + "="*60)
    print("CREANDO TIPOS DE ESTADO")
    print("="*60)
    
    tipos_datos = [
        ('DANADO', 'Dañado', 'danado', 'no_disponible', '#FF0000'),
        ('REPARACION', 'En Reparación', 'reparacion', 'no_disponible', '#FFA500'),
        ('OBSOLETO', 'Obsoleto', 'obsoleto', 'no_disponible', '#808080'),
        ('CALIBRACION', 'Calibración Pendiente', 'calibracion', 'disponible_restringido', '#FFFF00'),
        ('PREVENTIVO', 'Mantenimiento Preventivo', 'preventivo', 'parcialmente_disponible', '#FFC0CB'),
        ('OPERATIVO', 'Operativo', 'otro', 'disponible_restringido', '#90EE90'),
        ('DEFECTO', 'Defecto Menor', 'danado', 'disponible_restringido', '#FFD700'),
        ('PENDIENTE', 'Pendiente Revisión', 'otro', 'disponible_restringido', '#87CEEB'),
        ('RETIRO', 'Pendiente de Retiro', 'otro', 'no_disponible', '#D3D3D3'),
        ('ARCHIVO', 'Archivado', 'obsoleto', 'no_disponible', '#696969'),
    ]
    
    tipos_estado = []
    for codigo, nombre, categoria, impacto, color in tipos_datos:
        tipo, created = TipoEstado.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': categoria,
                'impacto_disponibilidad': impacto,
                'color': color,
                'descripcion': f'Estado: {nombre}',
                'activo': True
            }
        )
        tipos_estado.append(tipo)
        if created:
            print(f"✓ Tipo de Estado creado: {codigo} - {nombre}")
        else:
            print(f"→ Tipo de Estado ya existe: {codigo}")
    
    return tipos_estado


def crear_mantenimientos(productos, tipos_estado):
    """Crear 10 registros de mantenimiento."""
    print("\n" + "="*60)
    print("CREANDO REGISTROS DE MANTENIMIENTO")
    print("="*60)
    
    tipos_mantenimiento = ['correctivo', 'preventivo', 'calibracion', 'reparacion_externa', 'otro']
    prioridades = ['baja', 'media', 'alta', 'critica']
    
    mantenimientos = []
    for i in range(1, 11):
        producto = random.choice(productos)
        tipo_estado = random.choice(tipos_estado)
        fecha_reporte = timezone.now().date() - timedelta(days=random.randint(1, 30))
        fecha_inicio = fecha_reporte + timedelta(days=random.randint(1, 5))
        
        mant, created = Mantenimiento.objects.get_or_create(
            pk=i,  # Usar ID para asegurar que no se repita
            defaults={
                'producto': producto,
                'tipo_estado': tipo_estado,
                'tipo_mantenimiento': random.choice(tipos_mantenimiento),
                'estado_registro': random.choice(['abierto', 'en_proceso', 'cerrado']),
                'prioridad': random.choice(prioridades),
                'fecha_reporte': fecha_reporte,
                'fecha_inicio': fecha_inicio,
                'descripcion_problema': f'Problema detectado en {producto.nombre} - Reporte #{i}',
                'acciones_realizadas': f'Se realizaron acciones de mantenimiento en el producto',
                'costo_estimado': Decimal(random.randint(50000, 500000)),
            }
        )
        mantenimientos.append(mant)
        if created:
            print(f"✓ Mantenimiento {i} creado: {producto.nombre}")
        else:
            print(f"→ Mantenimiento {i} ya existe")
    
    return mantenimientos


def crear_prestamos(usuarios, productos):
    """Crear 10 préstamos."""
    print("\n" + "="*60)
    print("CREANDO PRÉSTAMOS")
    print("="*60)
    
    estados = ['pendiente', 'activo', 'parcial', 'devuelto', 'vencido']
    
    prestamos = []
    for i in range(1, 11):
        usuario = random.choice(usuarios)
        fecha_venc = timezone.now().date() + timedelta(days=random.randint(1, 30))
        
        prestamo, created = Prestamo.objects.get_or_create(
            pk=i,
            defaults={
                'usuario': usuario.numero_documento,
                'nombre_usuario': usuario.nombre_completo,
                'estado': random.choice(estados),
                'observaciones': f'Préstamo de prueba #{i}',
                'motivo_solicitud': 'Solicitud de herramientas para proyecto',
                'fecha_vencimiento': fecha_venc,
                'hora_max_entrega': timezone.now().time()
            }
        )
        prestamos.append(prestamo)
        if created:
            print(f"✓ Préstamo {i} creado: {usuario.nombre_completo}")
        else:
            print(f"→ Préstamo {i} ya existe")
    
    return prestamos


def crear_items_prestamo(prestamos, productos):
    """Crear 10+ ítems de préstamo."""
    print("\n" + "="*60)
    print("CREANDO ÍTEMS DE PRÉSTAMO")
    print("="*60)
    
    items = []
    contador = 1
    for prestamo in prestamos:
        # Agregar 2-3 items por préstamo
        num_items = random.randint(2, 3)
        for j in range(num_items):
            producto = random.choice(productos)
            if producto.stock > 0:
                item, created = ItemPrestamo.objects.get_or_create(
                    pk=contador,
                    defaults={
                        'prestamo': prestamo,
                        'producto': producto,
                        'cantidad': random.randint(1, 3),
                        'serial_entregado': f'SN-{contador:05d}',
                        'devuelto': random.choice([True, False, False])
                    }
                )
                items.append(item)
                if created:
                    print(f"✓ Ítem {contador} creado: {producto.nombre} en Préstamo #{prestamo.id}")
                else:
                    print(f"→ Ítem {contador} ya existe")
                contador += 1
    
    return items


def crear_devoluciones(prestamos, items):
    """Crear 10 devoluciones."""
    print("\n" + "="*60)
    print("CREANDO DEVOLUCIONES")
    print("="*60)
    
    estados_dev = ['pendiente', 'aprobada', 'rechazada']
    
    devoluciones = []
    for i in range(1, 11):
        prestamo = random.choice(prestamos)
        
        devolucion, created = Devolucion.objects.get_or_create(
            pk=i,
            defaults={
                'prestamo': prestamo,
                'devolucion_total': random.choice([True, False]),
                'motivo': f'Motivo de devolución #{i}: Fin de uso de herramientas',
                'estado': random.choice(estados_dev)
            }
        )
        devoluciones.append(devolucion)
        
        # Agregar items a la devolución
        items_prestamo = ItemPrestamo.objects.filter(prestamo=prestamo)[:random.randint(1, 2)]
        if created and items_prestamo.exists():
            devolucion.items.set(items_prestamo)
            print(f"✓ Devolución {i} creada para Préstamo #{prestamo.id}")
        elif created:
            print(f"✓ Devolución {i} creada para Préstamo #{prestamo.id}")
        else:
            print(f"→ Devolución {i} ya existe")
    
    return devoluciones


def crear_reportes(usuarios):
    """Crear 10 reportes históricos."""
    print("\n" + "="*60)
    print("CREANDO REPORTES HISTÓRICOS")
    print("="*60)
    
    modulos = ['inventario', 'prestamos', 'devoluciones', 'mantenimiento', 'almacenamiento', 'usuarios']
    formatos = ['pdf', 'excel']
    
    reportes = []
    for i in range(1, 11):
        usuario = random.choice(usuarios)
        
        reporte, created = ReporteHistorial.objects.get_or_create(
            pk=i,
            defaults={
                'modulo': random.choice(modulos),
                'formato': random.choice(formatos),
                'nombre_archivo': f'reporte_{i}_{timezone.now():%Y%m%d_%H%M%S}',
                'generado_por': usuario.nombre_completo,
                'total_registros': random.randint(10, 100)
            }
        )
        reportes.append(reporte)
        if created:
            print(f"✓ Reporte {i} creado: {reporte.get_modulo_display()}")
        else:
            print(f"→ Reporte {i} ya existe")
    
    return reportes


def main():
    """Función principal para poblar la base de datos."""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  SCRIPT DE POBLACIÓN DE BASE DE DATOS".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Ejecutar poblamiento en orden
        usuarios = crear_usuarios()
        categorias = crear_categorias()
        productos = crear_productos(categorias)
        almacenes = crear_almacenes()
        estantes = crear_estantes(almacenes)
        tipos_estado = crear_tipos_estado()
        mantenimientos = crear_mantenimientos(productos, tipos_estado)
        prestamos = crear_prestamos(usuarios, productos)
        items = crear_items_prestamo(prestamos, productos)
        devoluciones = crear_devoluciones(prestamos, items)
        reportes = crear_reportes(usuarios)
        
        # Resumen final
        print("\n" + "="*60)
        print("RESUMEN DE POBLACIÓN")
        print("="*60)
        print(f"✓ Usuarios: {Usuario.objects.count()}")
        print(f"✓ Categorías: {Categoria.objects.count()}")
        print(f"✓ Productos: {Producto.objects.count()}")
        print(f"✓ Almacenes: {Almacen.objects.count()}")
        print(f"✓ Estantes: {Estante.objects.count()}")
        print(f"✓ Tipos de Estado: {TipoEstado.objects.count()}")
        print(f"✓ Mantenimientos: {Mantenimiento.objects.count()}")
        print(f"✓ Préstamos: {Prestamo.objects.count()}")
        print(f"✓ Ítems de Préstamo: {ItemPrestamo.objects.count()}")
        print(f"✓ Devoluciones: {Devolucion.objects.count()}")
        print(f"✓ Reportes: {ReporteHistorial.objects.count()}")
        print("="*60)
        print("\n✓ ¡Población completada exitosamente!")
        
    except Exception as e:
        print(f"\n✗ Error durante la población: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
