# mantenimiento/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import TipoEstado, Mantenimiento


# ══════════════════════════════════════════════
# TIPO DE ESTADO
# ══════════════════════════════════════════════

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
        # ← labels eliminados: eran de Mantenimiento, no de TipoEstado

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


# ══════════════════════════════════════════════
# MANTENIMIENTO
# ══════════════════════════════════════════════

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
            'descripcion_problema', 'acciones_realizadas',
            'responsable', 'costo_estimado', 'costo_real', 'estado_registro',
        ]
        widgets = {
            'producto':           forms.HiddenInput(),
            'tipo_mantenimiento': forms.Select(attrs={'class': 'form-select'}),
            'tipo_estado':        forms.Select(attrs={'class': 'form-select'}),
            'estado_registro':    forms.Select(attrs={'class': 'form-select'}),
            'responsable':        forms.Select(attrs={'class': 'form-select'}),
            'fecha_reporte':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_inicio':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin_estimada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin_real':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion_problema': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el problema o falla detectada...'}),
            'acciones_realizadas':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Acciones realizadas o planificadas...'}),
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
            'responsable':         'Responsable / Técnico',
            'costo_estimado':      'Costo estimado',
            'costo_real':          'Costo real',
            'estado_registro':     'Estado del registro',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tipo_estado'].queryset = TipoEstado.objects.filter(activo=True)
        self.fields['responsable'].queryset = (
            User.objects.filter(is_active=True).order_by('first_name', 'username')
        )
        self.fields['responsable'].label_from_instance = (
            lambda u: u.get_full_name() or u.username
        )

        # Prellenar búsqueda al editar
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

        return cleaned