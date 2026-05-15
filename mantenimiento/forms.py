# mantenimiento/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import (
    TipoEstado, TipoMantenimiento, Mantenimiento, MantenimientoCambio,
    
)
from inventario.models import Producto

# TIPO MANTENIMIENTO

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
    """
    Formulario para registrar/editar mantenimientos con validaciones mejoradas.
    Incluye mensajes de error claros y específicos por campo.
    """

    producto_busqueda = forms.CharField(
        required=False,
        label='Ítem / Herramienta',
        widget=forms.TextInput(attrs={
            'class':        'form-control',
            'placeholder':  'Buscar por código, nombre o serie...',
            'id':           'producto_busqueda',
            'autocomplete': 'off',
            'aria-label':   'Búsqueda de ítem o herramienta',
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
            'tipo_mantenimiento': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Tipo de mantenimiento',
            }),
            'tipo_estado':        forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Tipo de estado',
            }),
            'estado_registro':    forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Estado del registro',
            }),
            'prioridad':          forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Prioridad',
            }),
            'responsable':        forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Técnico responsable',
            }),
            'fecha_reporte':      forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'aria-label': 'Fecha de reporte',
            }),
            'fecha_inicio':       forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'aria-label': 'Fecha de inicio',
            }),
            'fecha_fin_estimada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'aria-label': 'Fecha fin estimada',
            }),
            'fecha_fin_real':     forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'aria-label': 'Fecha fin real',
            }),
            'descripcion_problema': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el problema o falla detectada en detalle...',
                'aria-label': 'Descripción del problema',
                'minlength': '10',
            }),
            'acciones_realizadas':  forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe las acciones realizadas o planificadas...',
                'aria-label': 'Acciones realizadas',
            }),
            'materiales_usados':    forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista materiales, repuestos, cantidades y costos...',
                'aria-label': 'Materiales usados',
            }),
            'notas_adicionales':    forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Comentarios, observaciones o información relevante...',
                'aria-label': 'Notas adicionales',
            }),
            'evidencia_adicional':  forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx',
                'aria-label': 'Evidencia adjunta',
            }),
            'tiempo_empleado_horas': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.25',
                'min': '0',
                'aria-label': 'Tiempo empleado en horas',
            }),
            'costo_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'aria-label': 'Costo estimado',
            }),
            'costo_real':     forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'aria-label': 'Costo real',
            }),
        }
        labels = {
            'tipo_mantenimiento':  '🔧 Tipo de mantenimiento *',
            'tipo_estado':         '📊 Tipo de estado actual *',
            'fecha_reporte':       '📅 Fecha de reporte / detección *',
            'fecha_inicio':        '⏱️ Fecha inicio mantenimiento *',
            'fecha_fin_estimada':  '📅 Fecha fin estimada',
            'fecha_fin_real':      '✅ Fecha fin real',
            'descripcion_problema':'📝 Descripción del problema / falla *',
            'acciones_realizadas': '✏️ Acciones realizadas / planificadas',
            'materiales_usados':   '🛠️ Materiales / repuestos usados',
            'notas_adicionales':   '💬 Notas adicionales / comentarios',
            'evidencia_adicional': '📎 Evidencia adjunta (fotos, PDF, etc.)',
            'tiempo_empleado_horas': '⏳ Tiempo empleado (horas)',
            'prioridad':           '⚠️ Prioridad / urgencia *',
            'responsable':         '👤 Responsable / Técnico *',
            'costo_estimado':      '💵 Costo estimado',
            'costo_real':          '💰 Costo real',
            'estado_registro':     '📌 Estado del registro *',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar querysets
        self.fields['tipo_mantenimiento'].queryset = TipoMantenimiento.objects.filter(
            activo=True
        ).order_by('nombre')
        self.fields['tipo_mantenimiento'].empty_label = "-- Selecciona un tipo --"
        
        self.fields['tipo_estado'].queryset = TipoEstado.objects.filter(activo=True)
        self.fields['tipo_estado'].empty_label = "-- Selecciona un estado --"
        
        self.fields['estado_registro'].empty_label = "-- Selecciona el estado --"
        
        self.fields['prioridad'].empty_label = "-- Selecciona la prioridad --"
        
        self.fields['responsable'].queryset = (
            User.objects.filter(is_active=True).order_by('first_name', 'username')
        )
        self.fields['responsable'].empty_label = "-- Selecciona un técnico --"
        self.fields['responsable'].label_from_instance = (
            lambda u: f"{u.get_full_name() or u.username} ({u.username})"
        )

        # Prellenar búsqueda de producto en caso de edición
        if self.instance.pk and self.instance.producto_id:
            p = self.instance.producto
            self.fields['producto_busqueda'].initial = f"[{p.codigo_sku}] {p.nombre}"

    def clean_producto(self):
        """Valida que el producto sea obligatorio y válido."""
        producto = self.cleaned_data.get('producto')
        if not producto:
            raise ValidationError(
                "🚫 El ítem/herramienta es obligatorio. "
                "Por favor busca y selecciona uno de la lista de sugerencias."
            )
        
        # Validar que el producto existe
        try:
            Producto.objects.get(pk=producto.pk)
        except Producto.DoesNotExist:
            raise ValidationError(
                "❌ El ítem/herramienta seleccionado ya no existe. "
                "Por favor selecciona otro."
            )
        
        return producto

    def clean_tipo_mantenimiento(self):
        """Valida tipo de mantenimiento."""
        tipo = self.cleaned_data.get('tipo_mantenimiento')
        if not tipo:
            raise ValidationError(
                "🔧 Debes seleccionar un tipo de mantenimiento. "
                "Opciones: Preventivo, Correctivo, Calibración, etc."
            )
        return tipo

    def clean_tipo_estado(self):
        """Valida tipo de estado."""
        estado = self.cleaned_data.get('tipo_estado')
        if not estado:
            raise ValidationError(
                "📊 Debes seleccionar el estado del equipo después del mantenimiento."
            )
        return estado

    def clean_fecha_reporte(self):
        """Valida fecha de reporte."""
        fecha = self.cleaned_data.get('fecha_reporte')
        if not fecha:
            raise ValidationError(
                "📅 La fecha de reporte es obligatoria. "
                "Indica cuándo se detectó el problema."
            )
        
        from datetime import date
        if fecha > date.today():
            raise ValidationError(
                "⏰ La fecha de reporte no puede ser en el futuro."
            )
        
        return fecha

    def clean_fecha_inicio(self):
        """Valida fecha de inicio."""
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if not fecha_inicio:
            raise ValidationError(
                "⏱️ La fecha de inicio es obligatoria. "
                "Indica cuándo comenzó el mantenimiento."
            )
        
        fecha_reporte = self.cleaned_data.get('fecha_reporte')
        if fecha_reporte and fecha_inicio < fecha_reporte:
            raise ValidationError(
                "❌ La fecha de inicio no puede ser anterior a la de reporte. "
                f"Reporte: {fecha_reporte}, Inicio debe ser >= {fecha_reporte}"
            )
        
        return fecha_inicio

    def clean_descripcion_problema(self):
        """Valida descripción del problema."""
        desc = self.cleaned_data.get('descripcion_problema')
        if not desc or not desc.strip():
            raise ValidationError(
                "📝 La descripción del problema es obligatoria. "
                "Describe en detalle qué falla presenta el equipo."
            )
        
        if len(desc.strip()) < 10:
            raise ValidationError(
                "✏️ La descripción es muy corta. "
                "Mínimo 10 caracteres. Describe el problema en detalle."
            )
        
        return desc

    def clean_responsable(self):
        """Valida responsable/técnico."""
        responsable = self.cleaned_data.get('responsable')
        if not responsable:
            raise ValidationError(
                "👤 Debes asignar un técnico responsable del mantenimiento."
            )
        return responsable

    def clean_estado_registro(self):
        """Valida estado del registro."""
        estado = self.cleaned_data.get('estado_registro')
        if not estado:
            raise ValidationError(
                "📌 El estado del registro es obligatorio."
            )
        return estado

    def clean_prioridad(self):
        """Valida prioridad."""
        prioridad = self.cleaned_data.get('prioridad')
        if not prioridad:
            raise ValidationError(
                "⚠️ La prioridad es obligatoria. "
                "Selecciona: Baja, Media, Alta o Crítica."
            )
        return prioridad

    def clean(self):
        """Validaciones cruzadas."""
        cleaned = super().clean()
        
        fecha_reporte = cleaned.get('fecha_reporte')
        fecha_inicio = cleaned.get('fecha_inicio')
        fecha_fin_estimada = cleaned.get('fecha_fin_estimada')
        fecha_fin_real = cleaned.get('fecha_fin_real')
        tiempo = cleaned.get('tiempo_empleado_horas')
        costo_estimado = cleaned.get('costo_estimado')
        costo_real = cleaned.get('costo_real')

        # Validar fechas en orden lógico
        if fecha_reporte and fecha_inicio and fecha_inicio < fecha_reporte:
            self.add_error(
                'fecha_inicio',
                f"❌ La fecha de inicio ({fecha_inicio}) no puede ser anterior "
                f"a la fecha de reporte ({fecha_reporte})."
            )

        if fecha_inicio and fecha_fin_estimada and fecha_fin_estimada < fecha_inicio:
            self.add_error(
                'fecha_fin_estimada',
                f"❌ La fecha estimada ({fecha_fin_estimada}) no puede ser anterior "
                f"a la fecha de inicio ({fecha_inicio})."
            )

        if fecha_inicio and fecha_fin_real and fecha_fin_real < fecha_inicio:
            self.add_error(
                'fecha_fin_real',
                f"❌ La fecha real ({fecha_fin_real}) no puede ser anterior "
                f"a la fecha de inicio ({fecha_inicio})."
            )

        # Validar números
        if tiempo is not None and tiempo < 0:
            self.add_error(
                'tiempo_empleado_horas',
                "⏳ El tiempo no puede ser negativo."
            )

        if costo_estimado is not None and costo_estimado < 0:
            self.add_error(
                'costo_estimado',
                "💵 El costo estimado no puede ser negativo."
            )

        if costo_real is not None and costo_real < 0:
            self.add_error(
                'costo_real',
                "💰 El costo real no puede ser negativo."
            )

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