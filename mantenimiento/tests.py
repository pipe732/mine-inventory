from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from inventario.models import Producto
from .forms import MantenimientoUpdateForm
from .models import Mantenimiento, MantenimientoCambio, TipoEstado, TipoMantenimiento
class MantenimientoDisponibilidadTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='test1234',
        )
        self.producto = Producto.objects.create(
            codigo_sku='SKU-001',
            nombre='Taladro',
            stock=1,
            disponible=True,
            ubicacion='A1',
        )
    
        self.tipo_mantenimiento_correctivo, _ = TipoMantenimiento.objects.get_or_create(
            nombre='Correctivo',
            defaults={
                'descripcion': 'Tipo de mantenimiento correctivo usado en pruebas',
                'color': '#d9534f',
                'activo': True,
                'creado_por': self.user,
            },
        )
        self.estado_no_disponible, _ = TipoEstado.objects.get_or_create(
            codigo='DS',
            defaults={
                'nombre': 'Dañado severo',
                'categoria': 'danado',
                'impacto_disponibilidad': 'no_disponible',
                'activo': True,
            },
        )
        self.estado_restringido, _ = TipoEstado.objects.get_or_create(
            codigo='UR',
            defaults={
                'nombre': 'Uso restringido',
                'categoria': 'otro',
                'impacto_disponibilidad': 'disponible_restringido',
                'activo': True,
            },
        )

    def _crear_mantenimiento(self, estado='abierto', tipo_estado=None):
        # El campo tipo_mantenimiento ya es ForeignKey, así que debemos pasar
        # una instancia real del catálogo y no una cadena de texto.
        return Mantenimiento.objects.create(
            producto=self.producto,
            tipo_estado=tipo_estado or self.estado_no_disponible,
            responsable=self.user,
            creado_por=self.user,
            tipo_mantenimiento=self.tipo_mantenimiento_correctivo,
            estado_registro=estado,
            fecha_reporte=date(2026, 4, 10),
            fecha_inicio=date(2026, 4, 10),
            descripcion_problema='Falla de prueba',
        )

    def test_crear_mantenimiento_activo_no_disponible_bloquea_producto(self):
        self._crear_mantenimiento(estado='abierto')
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.disponible)

    def test_cerrar_mantenimiento_unico_habilita_producto(self):
        m = self._crear_mantenimiento(estado='abierto')
        m.estado_registro = 'cerrado'
        m.save()

        self.producto.refresh_from_db()
        self.assertTrue(self.producto.disponible)

    def test_cerrar_un_mantenimiento_no_habilita_si_hay_otro_activo(self):
        m1 = self._crear_mantenimiento(estado='abierto')
        self._crear_mantenimiento(estado='en_proceso')

        m1.estado_registro = 'cerrado'
        m1.save()

        self.producto.refresh_from_db()
        self.assertFalse(self.producto.disponible)

    def test_eliminar_mantenimiento_recalcula_disponibilidad(self):
        m = self._crear_mantenimiento(estado='abierto')
        m.delete()

        self.producto.refresh_from_db()
        self.assertTrue(self.producto.disponible)

    def test_mantenimiento_restringido_no_bloquea_disponibilidad(self):
        self._crear_mantenimiento(
            estado='abierto',
            tipo_estado=self.estado_restringido,
        )
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.disponible)

    def test_registrar_cambio_crea_log_auditoria(self):
        m = self._crear_mantenimiento(estado='abierto')
        m.registrar_cambio(
            editado_por=self.user,
            motivo_edicion='correccion_error',
            cambios={'estado_registro': {'anterior': 'abierto', 'nuevo': 'en_proceso'}},
            detalle_motivo='Ajuste inicial',
        )

        cambio = MantenimientoCambio.objects.get(mantenimiento=m)
        self.assertEqual(cambio.editado_por, self.user)
        self.assertEqual(cambio.motivo_edicion, 'correccion_error')
        self.assertIn('estado_registro', cambio.cambios)

    def test_formulario_edicion_detecta_cambios(self):
        m = self._crear_mantenimiento(estado='abierto')
        form = MantenimientoUpdateForm(
            data={
                'producto': self.producto.pk,
                'tipo_mantenimiento': self.tipo_mantenimiento_correctivo.pk,
                'tipo_estado': self.estado_no_disponible.pk,
                'fecha_reporte': '2026-04-10',
                'fecha_inicio': '2026-04-10',
                'fecha_fin_estimada': '',
                'fecha_fin_real': '',
                'descripcion_problema': 'Falla de prueba',
                'acciones_realizadas': 'Ajuste de correa',
                'materiales_usados': '',
                'notas_adicionales': '',
                'tiempo_empleado_horas': '2.5',
                'prioridad': 'media',
                'responsable': self.user.pk,
                'costo_estimado': '',
                'costo_real': '',
                'estado_registro': 'en_proceso',
                'motivo_edicion': 'actualizacion_imprevisto',
                'detalle_motivo': 'Cambio validado en diagnóstico',
                'confirmar_cambios': 'on',
            },
            instance=m,
            rol_usuario='supervisor',
            usuario_documento=self.user.username,
        )

        self.assertTrue(form.is_valid(), form.errors.as_json())
        cambios = form.get_changed_fields()
        self.assertIn('estado_registro', cambios)
        self.assertIn('acciones_realizadas', cambios)
