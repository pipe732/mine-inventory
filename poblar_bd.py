import os
import django

# Configurar el entorno de Django antes de importar cualquier modelo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import random
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Importación de modelos
from usuario.models import Usuario
from inventario.models import Categoria, Producto
from prestamo.models import Prestamo
from devoluciones.models import Devolucion

print("--- INICIANDO POBLACIÓN DE LA BASE DE DATOS ---")

# 1. CREAR USUARIO ADMINISTRADOR REQUERIDO
admin_doc = '0000000000'
admin_user, admin_created = Usuario.objects.get_or_create(
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
    print(f"[*] Administrador creado con éxito: {admin_doc} | a@b.com")
else:
    print(f"[*] El administrador ya existe: {admin_doc}")

# 2. CREAR 10 USUARIOS DE EJEMPLO
usuarios = []
for i in range(1, 11):
    doc = f'10000000{i:02d}'
    u, created = Usuario.objects.get_or_create(
        numero_documento=doc,
        defaults={
            'tipo_documento': 'CC',
            'nombre_completo': f'Usuario de Prueba {i}',
            'correo': f'usuario{i}@ejemplo.com',
            'rol': 'Usuario',
            'password': make_password('Usuario123*'),
            'telefono': f'31000000{i:02d}'
        }
    )
    usuarios.append(u)
print("[*] 10 Usuarios de ejemplo verificados/creados.")

# 3. CREAR 10 CATEGORÍAS
categorias = []
for i in range(1, 11):
    cat, _ = Categoria.objects.get_or_create(
        # Nota: Si tu campo llave se llama diferente a 'nombre', cámbialo aquí
        nombre=f'Categoría de prueba {i}',
    )
    categorias.append(cat)
print("[*] 10 Categorías de ejemplo verificadas/creadas.")

# 4. CREAR 10 PRODUCTOS
productos = []
for i in range(1, 11):
    prod, _ = Producto.objects.get_or_create(
        codigo_sku=f'SKU-PRB-{i:03d}',
        defaults={
            'nombre': f'Producto de prueba {i}',
            'categoria': categorias[i - 1],
            'stock': random.randint(10, 50),
            'ubicacion': f'Estante {i}',
        }
    )
    productos.append(prod)
print("[*] 10 Productos de ejemplo verificados/creados.")

# 5. CREAR 10 PRÉSTAMOS
prestamos = []
estados_prestamo = ['activo', 'vencido', 'pendiente', 'devuelto', 'parcial']
for i in range(1, 11):
    prestamo, _ = Prestamo.objects.get_or_create(
        id=i,  # Usamos un ID fijo del 1 al 10 para encontrarlos fácil
        defaults={
            'usuario': random.choice(usuarios),
            'estado': random.choice(estados_prestamo),
        }
    )
    prestamos.append(prestamo)
print("[*] 10 Préstamos de ejemplo verificados/creados.")

# 6. CREAR 10 DEVOLUCIONES
for i in range(1, 11):
    Devolucion.objects.get_or_create(
        prestamo=prestamos[i - 1],
        defaults={'estado': 'pendiente'}
    )
print("[*] 10 Devoluciones de ejemplo verificadas/creadas.")
print("--- PROCESO FINALIZADO ---")