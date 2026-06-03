#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo completos.
Genera mínimo 10+ registros por tabla para todos los módulos del sistema.

Módulos poblados:
  - usuario: Usuario (admin + 10 usuarios de prueba)
  - almacenamiento: Almacén, Estante
  - inventario: Categoría, Producto
  - prestamo: Préstamo, ItemPrestamo
  - devoluciones: Devolucion
  - mantenimiento: TipoEstado, Mantenimiento
  - reportes: ReporteHistorial

Uso:
  python poblar_bd_completo.py
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta, time
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction

# Importar modelos
from usuario.models import Usuario
from almacenamiento.models import Almacen, Estante
from inventario.models import Categoria, Producto
from mantenimiento.models import TipoEstado, Mantenimiento, TipoMantenimiento
from prestamo.models import Prestamo, ItemPrestamo
from devoluciones.models import Devolucion
from reportes.models import ReporteHistorial


def crear_usuarios():
    """Crear usuario admin y 15 usuarios de ejemplo."""
    print("\n" + "="*70)
    print("► CREANDO USUARIOS")
    print("="*70)
    
    # Crear usuario admin
    admin_doc = '0000000000'
    admin, admin_created = Usuario.objects.get_or_create(
        numero_documento=admin_doc,
        defaults={
            'tipo_documento': 'CC',
            'nombre_completo': 'Administrador Principal',
            'correo': 'admin@mineinventory.com',
            'rol': 'Administrador',
            'password': make_password('@dmin123'),
            'telefono': '3000000000',
            'numero_ficha': 'ADMIN-001',
            'nombre_programa': 'Administración'
        }
    )
    if admin_created:
        print(f"✓ Admin creado: {admin_doc} | admin@mineinventory.com")
    else:
        print(f"→ Admin ya existe: {admin_doc}")
    
    # Nombres y datos para usuarios de prueba
    nombres_usuarios = [
        ('Juan', 'Pérez'),
        ('María', 'García'),
        ('Carlos', 'López'),
        ('Ana', 'Martínez'),
        ('Roberto', 'González'),
        ('Sofía', 'Rodríguez'),
        ('Miguel', 'Hernández'),
        ('Isabella', 'Torres'),
        ('David', 'Ramírez'),
        ('Laura', 'Cruz'),
        ('Fernando', 'Morales'),
        ('Catalina', 'Soto'),
        ('Pablo', 'Gómez'),
        ('Valentina', 'Acosta'),
        ('Andrés', 'Vargas'),
    ]
    
    usuarios = [admin]
    for idx, (nombre, apellido) in enumerate(nombres_usuarios, 1):
        doc = f'1000000{idx:03d}'
        correo = f"{nombre.lower()}.{apellido.lower()}@sena.edu.co"
        
        usuario, created = Usuario.objects.get_or_create(
            numero_documento=doc,
            defaults={
                'tipo_documento': 'CC',
                'nombre_completo': f'{nombre} {apellido}',
                'correo': correo,
                'rol': 'Usuario',
                'password': make_password('Contra123*'),
                'telefono': f'310000{idx:04d}',
                'numero_ficha': f'FICHA-{idx:05d}',
                'nombre_programa': random.choice(['Minería', 'Construcción', 'Mecánica', 'Electricidad'])
            }
        )
        usuarios.append(usuario)
        if created:
            print(f"✓ Usuario {idx} creado: {nombre} {apellido} ({doc})")
        else:
            print(f"→ Usuario ya existe: {doc}")
    
    return usuarios


def crear_categorias():
    """Crear 15 categorías de productos."""
    print("\n" + "="*70)
    print("► CREANDO CATEGORÍAS DE PRODUCTOS")
    print("="*70)
    
    nombres_categorias = [
        'Herramientas Manuales',
        'Herramientas Eléctricas',
        'Equipos de Seguridad',
        'Equipos de Medición',
        'Tuberías y Accesorios',
        'Suministros de Construcción',
        'Equipos de Laboratorio',
        'Herramientas de Precisión',
        'Equipos de Protección Personal',
        'Materiales de Minería',
        'Accesorios Eléctricos',
        'Equipo de Ventilación',
        'Sistemas de Iluminación',
        'Herramientas Hidráulicas',
        'Materiales de Emergencia',
    ]
    
    categorias = []
    for nombre in nombres_categorias:
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Categoría de {nombre.lower()}'}
        )
        categorias.append(cat)
        if created:
            print(f"✓ Categoría: {nombre}")
        else:
            print(f"→ Categoría ya existe: {nombre}")
    
    return categorias


def crear_productos(categorias):
    """Crear 30+ productos variados."""
    print("\n" + "="*70)
    print("► CREANDO PRODUCTOS E INVENTARIO")
    print("="*70)
    
    productos_datos = [
        ('MART-001', 'Martillo de Goma 32 oz', 'Martillo para trabajos generales', 35, 'Herramientas Manuales'),
        ('DEST-SET', 'Set Destornilladores 12 pcs', 'Set completo de destornilladores', 20, 'Herramientas Manuales'),
        ('TALD-20V', 'Taladro Inalámbrico 20V', 'Taladro compacto y versátil', 12, 'Herramientas Eléctricas'),
        ('CASC-001', 'Casco de Seguridad Amarillo', 'Casco ANSI Z89.1', 50, 'Equipos de Seguridad'),
        ('MULT-001', 'Multímetro Digital 600V', 'Medidor digital profesional', 8, 'Equipos de Medición'),
        ('TUBO-PVC', 'Tubo PVC 1 Pulgada 3m', 'Tubo de PVC para agua', 75, 'Tuberías y Accesorios'),
        ('CEME-50K', 'Cemento Portland 50 kg', 'Cemento gris estándar', 150, 'Suministros de Construcción'),
        ('MICR-USB', 'Microscopio Digital USB', 'Microscopio de laboratorio con zoom', 5, 'Equipos de Laboratorio'),
        ('CALI-001', 'Calibrador Digital 0-150mm', 'Precisión de 0.01mm', 15, 'Herramientas de Precisión'),
        ('GUAN-NIT', 'Guantes de Nitrilo Azules', 'Caja de 100 guantes', 300, 'Equipos de Protección Personal'),
        ('LLAW-001', 'Juego Llaves Inglesas 8-32mm', 'Set de 8 llaves ajustables', 10, 'Herramientas Manuales'),
        ('SIER-CIR', 'Sierra Circular 7.25 Pulgadas', 'Sierra profesional para corte', 6, 'Herramientas Eléctricas'),
        ('GAFAS-P', 'Gafas de Seguridad Panorámicas', 'Protección ocular total', 40, 'Equipos de Seguridad'),
        ('LINTE-LED', 'Linterna LED Recargable', 'Linterna industrial 1000 lumens', 25, 'Sistemas de Iluminación'),
        ('NIVEL-01', 'Nivel Láser Automático', 'Alcance 50 metros', 4, 'Equipos de Medición'),
        ('MATER-EXP', 'Explosivos de Minería Clase C', 'Explosivos para voladuras controladas', 50, 'Materiales de Minería'),
        ('CINTE-001', 'Cinta Métrica 25 metros', 'Cinta de acero chromado', 30, 'Herramientas Manuales'),
        ('BOMBAS-H', 'Bomba Hidráulica Portátil', 'Capacidad 10 toneladas', 7, 'Herramientas Hidráulicas'),
        ('VENTI-01', 'Ventilador Industrial 18 pulgadas', 'Ventilación en espacios cerrados', 12, 'Equipo de Ventilación'),
        ('RECEP-E', 'Receptáculo Eléctrico IP67', 'Resistente a agua y polvo', 80, 'Accesorios Eléctricos'),
        ('ROPA-TR', 'Ropa de Trabajo Completa', 'Pantalón + Camisa talla L', 45, 'Equipos de Protección Personal'),
        ('POLEAS-01', 'Sistema de Poleas de Precision', 'Capacidad 500 kg', 9, 'Herramientas Hidráulicas'),
        ('MASCA-R', 'Máscara Respiratoria N95', 'Caja de 50 unidades', 200, 'Equipos de Seguridad'),
        ('PILAS-AA', 'Pilas AA Alcalinas', 'Pack de 24 pilas', 120, 'Materiales de Emergencia'),
        ('CABLE-1', 'Cable Eléctrico 2.5mm Naranja', 'Carrete de 100 metros', 20, 'Accesorios Eléctricos'),
        ('PERNO-01', 'Pernos de Anclaje M10', 'Caja de 100 unidades', 500, 'Suministros de Construcción'),
        ('TESTER-01', 'Probador de Voltaje sin Contacto', 'Detecta 12-1000V', 14, 'Equipos de Medición'),
        ('LINEA-PL', 'Línea de Vida y Arnés', 'Equipo anticaída completo', 8, 'Equipos de Seguridad'),
        ('CLAVE-EX', 'Llave Hexagonal Set 27 pcs', 'Allen keys variadas', 16, 'Herramientas Manuales'),
        ('TUERCA-M', 'Tuercas Variadas Mix', 'Caja con 500 tuercas', 80, 'Suministros de Construcción'),
    ]
    
    # Mapear nombres de categorías a objetos
    cat_map = {cat.nombre: cat for cat in categorias}
    
    productos = []
    contador = 0
    for sku, nombre, desc, stock, cat_nombre in productos_datos:
        cat = cat_map.get(cat_nombre, categorias[0])
        prod, created = Producto.objects.get_or_create(
            codigo_sku=sku,
            defaults={
                'nombre': nombre,
                'descripcion': desc,
                'stock': stock,
                'categoria': cat,
                'numero_serie': f'SN-{sku}-{random.randint(10000, 99999)}',
                'disponible': True,
                'ubicacion': 'Almacén Principal'
            }
        )
        productos.append(prod)
        if created:
            contador += 1
            print(f"✓ Producto: {sku:15s} {nombre[:35]:35s} Stock: {stock:4d}")
        else:
            print(f"→ Producto ya existe: {sku}")
    
    print(f"\n✓ Total productos creados: {contador}")
    return productos


def crear_almacenes():
    """Crear 10+ almacenes."""
    print("\n" + "="*70)
    print("► CREANDO ALMACENES")
    print("="*70)
    
    almacenes_datos = [
        ('Almacén Principal', 'Ubicado en planta baja, acceso principal'),
        ('Almacén de Herramientas', 'Herramientas manuales y eléctricas'),
        ('Almacén de Seguridad', 'Equipos de protección personal'),
        ('Almacén de Materiales', 'Tuberías, cemento y suministros'),
        ('Almacén de Laboratorio', 'Equipos de medición y precisión'),
        ('Bóveda de Explosivos', 'Materiales controlados de minería'),
        ('Almacén de Respaldo', 'Stock de reserva y emergencias'),
        ('Almacén Temporal', 'Recepción y clasificación'),
        ('Almacén Climatizado', 'Equipo sensible a temperatura'),
        ('Zona de Reparación', 'Equipo en mantenimiento'),
        ('Depósito Exterior', 'Materiales voluminosos'),
    ]
    
    almacenes = []
    for nombre, detalles in almacenes_datos:
        almacen, created = Almacen.objects.get_or_create(
            nombre=nombre,
            defaults={
                'detalles': detalles,
                'capacidad': random.randint(500, 5000)
            }
        )
        almacenes.append(almacen)
        if created:
            print(f"✓ Almacén: {nombre:25s} Capacidad: {almacen.capacidad:5d} m³")
        else:
            print(f"→ Almacén ya existe: {nombre}")
    
    return almacenes


def crear_estantes(almacenes):
    """Crear 30+ estantes distribuidos en almacenes."""
    print("\n" + "="*70)
    print("► CREANDO ESTANTES")
    print("="*70)
    
    estantes = []
    contador = 1
    
    # Crear 3-4 estantes por almacén
    for almacen in almacenes:
        num_estantes = random.randint(2, 4)
        for i in range(1, num_estantes + 1):
            estante, created = Estante.objects.get_or_create(
                codigo=f'EST-{almacen.id:02d}-{i:02d}',
                defaults={
                    'almacen': almacen,
                    'detalles': f'Estante nivel {i} - {almacen.nombre}',
                    'capacidad': random.randint(100, 500)
                }
            )
            estantes.append(estante)
            if created:
                print(f"✓ Estante {contador:3d}: EST-{almacen.id:02d}-{i:02d} | {almacen.nombre:25s} Cap: {estante.capacidad}")
                contador += 1
            else:
                print(f"→ Estante ya existe: EST-{almacen.id:02d}-{i:02d}")
    
    print(f"\n✓ Total estantes creados: {len(estantes)}")
    return estantes


def crear_tipos_estado():
    """Crear 12 tipos de estado de mantenimiento."""
    print("\n" + "="*70)
    print("► CREANDO TIPOS DE ESTADO DE MANTENIMIENTO")
    print("="*70)
    
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
        ('BLOQUEADO', 'Bloqueado', 'reparacion', 'no_disponible', '#8B0000'),
        ('LIMPIAR', 'Requiere Limpieza', 'otro', 'disponible_restringido', '#C0C0C0'),
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
            print(f"✓ Estado: {codigo:15s} {nombre:30s} ({impacto})")
        else:
            print(f"→ Estado ya existe: {codigo}")
    
    return tipos_estado


def crear_tipos_mantenimiento():
    """Crear tipos de mantenimiento si no existen."""
    print("\n" + "="*70)
    print("► CREANDO TIPOS DE MANTENIMIENTO")
    print("="*70)
    
    tipos_datos = [
        ('Mantenimiento Correctivo', 'Reparación de daños'),
        ('Mantenimiento Preventivo', 'Prevención de daños'),
        ('Calibración', 'Ajuste de precisión'),
        ('Reparación Externa', 'Enviado a terceros'),
        ('Revisión General', 'Inspección completa'),
    ]
    
    tipos = []
    contador = 0
    for nombre, descripcion in tipos_datos:
        tipo, created = TipoMantenimiento.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': descripcion,
                'activo': True
            }
        )
        tipos.append(tipo)
        if created:
            print(f"✓ Tipo: {nombre}")
            contador += 1
        else:
            print(f"→ Tipo ya existe: {nombre}")
    
    return tipos


def crear_usuarios_django():
    """Crear usuarios de Django (auth.User) para asignarlos como responsables."""
    print("\n" + "="*70)
    print("► CREANDO USUARIOS DJANGO (auth.User)")
    print("="*70)
    
    usuarios_datos = [
        ('juan_perez', 'Juan', 'Pérez', 'juan@mineinventory.com'),
        ('maria_garcia', 'María', 'García', 'maria@mineinventory.com'),
        ('carlos_lopez', 'Carlos', 'López', 'carlos@mineinventory.com'),
        ('ana_martinez', 'Ana', 'Martínez', 'ana@mineinventory.com'),
        ('roberto_gonzalez', 'Roberto', 'González', 'roberto@mineinventory.com'),
    ]
    
    usuarios = []
    for username, first_name, last_name, email in usuarios_datos:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
        )
        usuarios.append(user)
        if created:
            print(f"✓ Usuario Django: {username} ({first_name} {last_name})")
        else:
            print(f"→ Usuario Django ya existe: {username}")
    
    return usuarios


def crear_mantenimientos(productos, tipos_estado, usuarios_django):
    """Crear 25+ registros de mantenimiento."""
    print("\n" + "="*70)
    print("► CREANDO REGISTROS DE MANTENIMIENTO")
    print("="*70)
    
    tipos_mant_nombres = [
        'Mantenimiento Correctivo', 
        'Mantenimiento Preventivo', 
        'Calibración', 
        'Reparación Externa', 
        'Revisión General'
    ]
    prioridades = ['baja', 'media', 'alta', 'critica']
    estados_registro = ['abierto', 'en_proceso', 'cerrado', 'pendiente']
    
    # Obtener todas las instancias de TipoMantenimiento
    tipos_mant_objs = TipoMantenimiento.objects.filter(nombre__in=tipos_mant_nombres)
    
    # Usar los usuarios de Django pasados como parámetro
    if not usuarios_django:
        print("✗ No hay usuarios de Django disponibles para asignar como responsables")
        return []
    
    mantenimientos = []
    for i in range(1, 26):
        try:
            producto = random.choice(productos)
            tipo_estado = random.choice(tipos_estado)
            responsable = random.choice(usuarios_django)
            creado_por = random.choice(usuarios_django)
            fecha_reporte = timezone.now().date() - timedelta(days=random.randint(1, 60))
            fecha_inicio = fecha_reporte + timedelta(days=random.randint(1, 5))
            
            # Obtener una instancia aleatoria de TipoMantenimiento
            tipo_mant_obj = random.choice(tipos_mant_objs)
            
            mant, created = Mantenimiento.objects.get_or_create(
                pk=i,
                defaults={
                    'producto': producto,
                    'tipo_estado': tipo_estado,
                    'tipo_mantenimiento': tipo_mant_obj,
                    'estado_registro': random.choice(estados_registro),
                    'prioridad': random.choice(prioridades),
                    'fecha_reporte': fecha_reporte,
                    'fecha_inicio': fecha_inicio,
                    'descripcion_problema': f'Problema detectado en {producto.nombre} durante inspección',
                    'acciones_realizadas': 'Se realizaron acciones de mantenimiento correctivas',
                    'costo_estimado': Decimal(random.randint(50000, 500000)),
                    'responsable': responsable,
                    'creado_por': creado_por
                }
            )
            mantenimientos.append(mant)
            if created:
                print(f"✓ Mant #{i:2d}: {producto.nombre[:30]:30s} | {tipo_estado.codigo:15s} | {mant.prioridad}")
            else:
                print(f"→ Mantenimiento ya existe: ID {i}")
        except Exception as e:
            print(f"✗ Error creando mantenimiento {i}: {str(e)}")
    
    print(f"\n✓ Total mantenimientos creados: {len(mantenimientos)}")
    return mantenimientos


def crear_prestamos(usuarios, productos):
    """Crear 20+ préstamos."""
    print("\n" + "="*70)
    print("► CREANDO PRÉSTAMOS")
    print("="*70)
    
    estados = ['pendiente', 'activo', 'parcial', 'devuelto', 'vencido', 'rechazado']
    
    prestamos = []
    contador = 1
    for i in range(1, 21):
        try:
            usuario = random.choice(usuarios[1:])  # Excluir admin
            fecha_venc = timezone.now().date() + timedelta(days=random.randint(1, 30))
            
            prestamo, created = Prestamo.objects.get_or_create(
                pk=i,
                defaults={
                    'usuario': usuario.numero_documento,
                    'nombre_usuario': usuario.nombre_completo,
                    'estado': random.choice(estados),
                    'observaciones': f'Préstamo para proyecto de {usuario.nombre_programa}',
                    'motivo_solicitud': random.choice([
                        'Solicitud de herramientas para mantenimiento',
                        'Herramientas para proyecto de construcción',
                        'Equipos para capacitación',
                        'Materiales para reparación de equipos',
                        'Préstamo para inspección'
                    ]),
                    'fecha_vencimiento': fecha_venc,
                    'hora_max_entrega': time(16, 0)
                }
            )
            prestamos.append(prestamo)
            if created:
                print(f"✓ Préstamo #{i:2d}: {usuario.nombre_completo:25s} | {prestamo.estado:12s} | Vence: {fecha_venc}")
                contador += 1
            else:
                print(f"→ Préstamo ya existe: ID {i}")
        except Exception as e:
            print(f"✗ Error creando préstamo {i}: {str(e)}")
    
    print(f"\n✓ Total préstamos creados: {contador}")
    return prestamos


def crear_items_prestamo(prestamos, productos):
    """Crear 50+ ítems de préstamo."""
    print("\n" + "="*70)
    print("► CREANDO ÍTEMS DE PRÉSTAMO")
    print("="*70)
    
    items = []
    contador = 1
    for prestamo in prestamos:
        try:
            # Agregar 2-4 items por préstamo
            num_items = random.randint(2, 4)
            for j in range(num_items):
                producto = random.choice(productos)
                if producto.stock > 0:
                    cantidad = min(random.randint(1, 3), producto.stock)
                    
                    item, created = ItemPrestamo.objects.get_or_create(
                        pk=contador,
                        defaults={
                            'prestamo': prestamo,
                            'producto': producto,
                            'cantidad': cantidad,
                            'serial_entregado': f'SN-{contador:06d}',
                            'devuelto': random.choice([True, True, True, False])
                        }
                    )
                    items.append(item)
                    if created:
                        status = "Devuelto" if item.devuelto else "Pendiente"
                        print(f"✓ Item #{contador:3d}: Préstamo #{prestamo.id:2d} | {producto.nombre[:25]:25s} x{cantidad} | {status}")
                    contador += 1
        except Exception as e:
            print(f"✗ Error creando items para préstamo {prestamo.id}: {str(e)}")
    
    print(f"\n✓ Total ítems de préstamo creados: {len(items)}")
    return items


def crear_devoluciones(prestamos, items):
    """Crear 15+ devoluciones."""
    print("\n" + "="*70)
    print("► CREANDO DEVOLUCIONES")
    print("="*70)
    
    devoluciones = []
    contador = 1
    for prestamo in prestamos[:15]:  # Primeros 15 préstamos
        try:
            devolucion, created = Devolucion.objects.get_or_create(
                pk=contador,
                defaults={
                    'prestamo': prestamo,
                    'devolucion_total': random.choice([True, False]),
                    'motivo': random.choice([
                        'Fin de uso de herramientas',
                        'Cambio de proyecto',
                        'Herramientas dañadas en uso',
                        'Uso completado satisfactoriamente',
                        'Devolución anticipada'
                    ])
                }
            )
            devoluciones.append(devolucion)
            
            # Agregar items a la devolución
            items_prestamo = ItemPrestamo.objects.filter(
                prestamo=prestamo,
                devuelto=True
            )[:random.randint(1, 3)]
            
            if created:
                if items_prestamo.exists():
                    devolucion.items.set(items_prestamo)
                    print(f"✓ Devolución #{contador:2d}: Préstamo #{prestamo.id:2d} | {devolucion.estado:12s} | {items_prestamo.count()} items")
                else:
                    print(f"✓ Devolución #{contador:2d}: Préstamo #{prestamo.id:2d} | {devolucion.estado:12s} | Sin items")
                contador += 1
            else:
                print(f"→ Devolución ya existe: ID {contador}")
        except Exception as e:
            print(f"✗ Error creando devolución para préstamo {prestamo.id}: {str(e)}")
    
    print(f"\n✓ Total devoluciones creadas: {len(devoluciones)}")
    return devoluciones


def crear_reportes(usuarios):
    """Crear 15+ reportes históricos."""
    print("\n" + "="*70)
    print("► CREANDO REPORTES HISTÓRICOS")
    print("="*70)
    
    modulos = [
        ('inventario', 'Reporte de Inventario'),
        ('prestamos', 'Reporte de Préstamos'),
        ('devoluciones', 'Reporte de Devoluciones'),
        ('mantenimiento', 'Reporte de Mantenimiento'),
        ('almacenamiento', 'Reporte de Almacenamiento'),
        ('usuarios', 'Reporte de Usuarios')
    ]
    formatos = ['pdf', 'excel']
    
    reportes = []
    contador = 1
    for i in range(1, 16):
        try:
            usuario = random.choice(usuarios[1:])
            modulo, nombre_mod = random.choice(modulos)
            formato = random.choice(formatos)
            
            reporte, created = ReporteHistorial.objects.get_or_create(
                pk=i,
                defaults={
                    'modulo': modulo,
                    'formato': formato,
                    'nombre_archivo': f'reporte_{modulo}_{timezone.now():%Y%m%d_%H%M%S}_{i}',
                    'generado_por': usuario.nombre_completo,
                    'total_registros': random.randint(20, 200)
                }
            )
            reportes.append(reporte)
            if created:
                formato_display = dict(ReporteHistorial.FORMATO_CHOICES).get(formato, formato)
                print(f"✓ Reporte #{i:2d}: {nombre_mod:30s} | {formato_display:5s} | {reporte.total_registros:3d} registros")
                contador += 1
            else:
                print(f"→ Reporte ya existe: ID {i}")
        except Exception as e:
            print(f"✗ Error creando reporte {i}: {str(e)}")
    
    print(f"\n✓ Total reportes creados: {contador}")
    return reportes


@transaction.atomic
def main():
    """Función principal para poblar la base de datos."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  POBLAR BASE DE DATOS - MINE INVENTORY".center(68) + "║")
    print("║" + "  Cargando datos de ejemplo para todos los módulos".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        # Ejecutar poblamiento en orden
        usuarios = crear_usuarios()
        usuarios_django = crear_usuarios_django()
        categorias = crear_categorias()
        productos = crear_productos(categorias)
        almacenes = crear_almacenes()
        estantes = crear_estantes(almacenes)
        tipos_estado = crear_tipos_estado()
        tipos_mant = crear_tipos_mantenimiento()
        mantenimientos = crear_mantenimientos(productos, tipos_estado, usuarios_django)
        prestamos = crear_prestamos(usuarios, productos)
        items = crear_items_prestamo(prestamos, productos)
        devoluciones = crear_devoluciones(prestamos, items)
        reportes = crear_reportes(usuarios)
        
        # Resumen final
        print("\n" + "="*70)
        print("RESUMEN FINAL DE POBLACIÓN")
        print("="*70)
        print(f"✓ Usuarios:              {Usuario.objects.count():4d}")
        print(f"✓ Categorías:            {Categoria.objects.count():4d}")
        print(f"✓ Productos:             {Producto.objects.count():4d}")
        print(f"✓ Almacenes:             {Almacen.objects.count():4d}")
        print(f"✓ Estantes:              {Estante.objects.count():4d}")
        print(f"✓ Tipos de Estado:       {TipoEstado.objects.count():4d}")
        print(f"✓ Mantenimientos:        {Mantenimiento.objects.count():4d}")
        print(f"✓ Préstamos:             {Prestamo.objects.count():4d}")
        print(f"✓ Ítems de Préstamo:     {ItemPrestamo.objects.count():4d}")
        print(f"✓ Devoluciones:          {Devolucion.objects.count():4d}")
        print(f"✓ Reportes:              {ReporteHistorial.objects.count():4d}")
        print("="*70)
        print("\n✓✓✓ ¡Población completada exitosamente! ✓✓✓\n")
        
    except Exception as e:
        print(f"\n✗ Error durante la población: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
