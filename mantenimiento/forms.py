# mantenimiento/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import (
    TipoEstado, TipoMantenimiento, Mantenimiento, MantenimientoCambio, ConsumoRepuesto,
    MOTIVO_CAMBIO_CHOICES
)
from inventario.models import Producto

# ─────────────────────────────────────────────────────────────
# TIPO MANTENIMIENTO
# ─────────────────────────────────────────────────────────────

class TipoMantenimientoForm(forms.ModelForm):
    """Formulario para crear y editar tipos de mantenimiento."""

    class Meta:
        model = TipoMantenimiento
        fields = ['nombre', 'descripcion', 'color', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Correctivo, Preventivo...',
                'maxlength': '50',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de mantenimiento (opcional)',
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'style': 'max-width: 100px;',
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'nombre': 'Nombre del tipo',
            'descripcion': 'Descripción',
            'color': 'Color (opcional)',
            'activo': 'Activo',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Validar unicidad
            qs = TipoMantenimiento.objects.filter(nombre__iexact=nombre)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ya existe un tipo de mantenimiento con este nombre.")
        return nombre


#tipo estado formulario
class TipoEstadoForm(forms.ModelForm):

    class Meta:
        model  = TipoEstado
        fields = ['nombre', 'codigo', 'descripcion', 'categoria',
                  'impacto_disponibilidad', 'color', 'activo']
        widgets = {
            'nombre':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Dañado severo'}),
            'codigo':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: DS'}),
            'descripcion':forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria':  forms.Select(attrs={'class': 'form-select'}),
            'impacto_disponibilidad': forms.Select(attrs={'class': 'form-select'}),
            'color':      forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-25'}),
            'activo':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            qs = TipoEstado.objects.filter(nombre__iexact=nombre)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ya existe un tipo de estado con este nombre.")
        return nombre

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            qs = TipoEstado.objects.filter(codigo__iexact=codigo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Este código ya está en uso.")
        return codigo

#mantenimiento 
class MantenimientoForm(forms.ModelForm):

    producto_busqueda = forms.CharField(
        required=False,
        label='Ítem / Herramienta',
        widget=forms.TextInput(attrs={
            'class':        'form-control',
            'placeholder':  'Buscar por código, nombre o serie...',
            'id':           'producto_busqueda',
            'autocomplete': 'off',
        }),
    )

    class Meta:
        model  = Mantenimiento
        fields = [
            'producto', 'tipo_mantenimiento', 'tipo_estado',
            'fecha_reporte', 'fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real',
            'descripcion_problema', 'acciones_realizadas', 'materiales_usados',
            'notas_adicionales', 'evidencia_adicional', 'tiempo_empleado_horas',
            'prioridad', 'responsable', 'costo_estimado', 'costo_real', 'estado_registro',
        ]
        widgets = {
            'producto':           forms.HiddenInput(),
            'tipo_mantenimiento': forms.Select(attrs={'class': 'form-select'}),
            'tipo_estado':        forms.Select(attrs={'class': 'form-select'}),
            'estado_registro':    forms.Select(attrs={'class': 'form-select'}),
            'prioridad':          forms.Select(attrs={'class': 'form-select'}),
            'responsable':        forms.Select(attrs={'class': 'form-select'}),
            'fecha_reporte':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_inicio':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin_estimada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin_real':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion_problema': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el problema o falla detectada...'}),
            'acciones_realizadas':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Acciones realizadas o planificadas...'}),
            'materiales_usados':    forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Materiales, repuestos y cantidades usadas...'}),
            'notas_adicionales':    forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comentarios adicionales...'}),
            'evidencia_adicional':  forms.FileInput(attrs={'class': 'form-control'}),
            'tiempo_empleado_horas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.25', 'min': '0'}),
            'costo_estimado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'costo_real':     forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }
        labels = {
            'tipo_mantenimiento':  'Tipo de mantenimiento',
            'tipo_estado':         'Tipo de estado actual',
            'fecha_reporte':       'Fecha de reporte / detección',
            'fecha_inicio':        'Fecha inicio mantenimiento',
            'fecha_fin_estimada':  'Fecha fin estimada',
            'fecha_fin_real':      'Fecha fin real',
            'descripcion_problema':'Descripción del problema / falla',
            'acciones_realizadas': 'Acciones realizadas / planificadas',
            'materiales_usados':   'Materiales / repuestos usados',
            'notas_adicionales':   'Notas adicionales / comentarios',
            'evidencia_adicional': 'Evidencia adjunta',
            'tiempo_empleado_horas': 'Tiempo empleado (horas hombre)',
            'prioridad':           'Prioridad / urgencia',
            'responsable':         'Responsable / Técnico',
            'costo_estimado':      'Costo estimado',
            'costo_real':          'Costo real',
            'estado_registro':     'Estado del registro',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tipo_mantenimiento'].queryset = TipoMantenimiento.objects.filter(
            activo=True
        ).order_by('nombre')
        self.fields['tipo_estado'].queryset = TipoEstado.objects.filter(activo=True)
        self.fields['responsable'].queryset = (
            User.objects.filter(is_active=True).order_by('first_name', 'username')
        )
        self.fields['responsable'].label_from_instance = (
            lambda u: u.get_full_name() or u.username
        )

        if self.instance.pk and self.instance.producto_id:
            p = self.instance.producto
            self.fields['producto_busqueda'].initial = f"[{p.codigo_sku}] {p.nombre}"

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        if not producto:
            raise ValidationError("Debes seleccionar un ítem o herramienta válido.")
        return producto

    def clean(self):
        cleaned            = super().clean()
        fecha_reporte      = cleaned.get('fecha_reporte')
        fecha_inicio       = cleaned.get('fecha_inicio')
        fecha_fin_estimada = cleaned.get('fecha_fin_estimada')
        fecha_fin_real     = cleaned.get('fecha_fin_real')

        if fecha_reporte and fecha_inicio and fecha_inicio < fecha_reporte:
            self.add_error('fecha_inicio', "No puede ser anterior a la fecha de reporte.")

        if fecha_inicio and fecha_fin_estimada and fecha_fin_estimada < fecha_inicio:
            self.add_error('fecha_fin_estimada', "No puede ser anterior a la fecha de inicio.")

        if fecha_inicio and fecha_fin_real and fecha_fin_real < fecha_inicio:
            self.add_error('fecha_fin_real', "No puede ser anterior a la fecha de inicio.")

        tiempo = cleaned.get('tiempo_empleado_horas')
        if tiempo is not None and tiempo < 0:
            self.add_error('tiempo_empleado_horas', "No puede ser negativo.")

        costo_real = cleaned.get('costo_real')
        costo_estimado = cleaned.get('costo_estimado')
        if costo_real is not None and costo_real < 0:
            self.add_error('costo_real', "No puede ser negativo.")
        if costo_estimado is not None and costo_estimado < 0:
            self.add_error('costo_estimado', "No puede ser negativo.")

        return cleaned


class MantenimientoUpdateForm(MantenimientoForm):
    MOTIVOS = MantenimientoCambio.MOTIVO_CHOICES

    CAMPOS_TECNICO_EDITABLES = {
        'acciones_realizadas',
        'materiales_usados',
        'notas_adicionales',
        'tiempo_empleado_horas',
        'evidencia_adicional',
    }

    motivo_edicion = forms.ChoiceField(
        label='Motivo de edición',
        choices=MOTIVOS,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    detalle_motivo = forms.CharField(
        label='Detalle del motivo (opcional)',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ej: ajuste de tiempos tras verificación en taller'}
        ),
    )
    confirmar_cambios = forms.BooleanField(
        label='Confirmo que revisé los cambios antes de guardar',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, **kwargs):
        self.rol_usuario = (kwargs.pop('rol_usuario', '') or '').strip().lower()
        self.usuario_documento = kwargs.pop('usuario_documento', '')
        super().__init__(*args, **kwargs)
        self._changed_fields_cache = None

        if 'tecnico' in self.rol_usuario:
            for field_name, field in self.fields.items():
                if field_name in {'motivo_edicion', 'detalle_motivo', 'confirmar_cambios'}:
                    continue
                if field_name not in self.CAMPOS_TECNICO_EDITABLES:
                    field.disabled = True

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('confirmar_cambios'):
            self.add_error('confirmar_cambios', 'Debes confirmar los cambios antes de guardar.')

        cambios = self.get_changed_fields()
        if not cambios:
            raise ValidationError('No se detectaron cambios para guardar.')

        motivo = cleaned.get('motivo_edicion')
        detalle = (cleaned.get('detalle_motivo') or '').strip()
        if motivo == 'otro' and not detalle:
            self.add_error('detalle_motivo', 'Debes detallar el motivo cuando seleccionas "Otro".')

        return cleaned

    def get_changed_fields(self):
        if self._changed_fields_cache is not None:
            return self._changed_fields_cache

        if not self.instance.pk:
            self._changed_fields_cache = {}
            return self._changed_fields_cache

        cambios = {}
        for field_name in self.changed_data:
            if field_name in {'motivo_edicion', 'detalle_motivo', 'confirmar_cambios', 'producto_busqueda'}:
                continue

            field = self.fields.get(field_name)
            if field is not None and field.disabled:
                continue

            old_value = getattr(self.instance, field_name, None)
            new_value = self.cleaned_data.get(field_name)

            if hasattr(old_value, 'pk'):
                old_value = old_value.pk
            if hasattr(new_value, 'pk'):
                new_value = new_value.pk

            if hasattr(old_value, 'isoformat'):
                old_value = old_value.isoformat()
            if hasattr(new_value, 'isoformat'):
                new_value = new_value.isoformat()

            if hasattr(new_value, 'name'):
                new_value = new_value.name
            if hasattr(old_value, 'name'):
                old_value = old_value.name

            if old_value != new_value:
                cambios[field_name] = {
                    'anterior': '' if old_value is None else str(old_value),
                    'nuevo': '' if new_value is None else str(new_value),
                }

        self._changed_fields_cache = cambios
        return cambios