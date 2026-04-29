{# GUÍA DE ESTRUCTURA DRY PARA PLANTILLAS DE MANTENIMIENTO #}
{# 
Este archivo documenta la estructura DRY (Don't Repeat Yourself) implementada
en los partials de mantenimiento. 

UBICACIÓN PRINCIPAL: 
  mantenimiento/templates/mantenimiento/partials/

ESTRUCTURA DEL MODELO MANTENIMIENTO:
====================================

mantenimiento/
├── static/
│   └── css/
│       └── mantenimiento-components.css      ← Estilos CSS centralizados (150 líneas)
├── templates/
│   └── mantenimiento/
│       ├── mantenimiento_form.html
│       ├── mantenimiento_lista.html
│       ├── estado_actual.html
│       ├── historial_producto.html
│       ├── mantenimiento_detalle.html
│       └── partials/
│           ├── _base_styles.html             ← Carga los estilos CSS
│           ├── _svg_icon.html                ← Componente de iconos
│           ├── _field_error.html             ← Render de errores
│           ├── _form_field.html              ← Campo genérico
│           ├── _filter_select.html           ← Select genérico
│           ├── _action_icon_button.html      ← Botones de acción
│           ├── _badge_estado_registro.html   ← Badge de estado
│           ├── _count_badge.html             ← Badge con contador
│           ├── _section_heading.html         ← Títulos de sección
│           ├── _tabla_empty.html             ← Tabla vacía
│           ├── _cabecera.html                ← Encabezado de página
│           ├── _filtros.html                 ← Filtros adaptativos
│           ├── _repuesto_row.html            ← Fila de repuesto
│           ├── _consumo_repuestos_formset.html
│           └── README_DRY_STRUCTURE.md       ← Este archivo

2. FILTROS Y BÚSQUEDA
   ├─ _filtros.html              → Filtros adaptativos (mantenimiento/historial/estado)
   └─ _filter_select.html        → Select genérico para filtros

3. COMPONENTES VISUALES
   ├─ _badge_estado_registro.html → Badge para estado del registro
   ├─ _count_badge.html          → Badge con contador
   ├─ _section_heading.html      → Títulos de sección estandarizados
   ├─ _tabla_empty.html          → Mensaje de tabla vacía
   ├─ _cabecera.html             → Encabezado de página con acciones
   └─ _action_icon_button.html   → Botones de acción con iconos

4. FORMULARIOS ESPECÍFICOS
   ├─ _repuesto_row.html         → Fila de consumo de repuesto
   └─ _consumo_repuestos_formset.html → Formset completo de repuestos

CLASES CSS DISPONIBLES:
=======================

Ubicación: mantenimiento/static/css/mantenimiento-components.css

.style-section-label       → Etiquetas de sección (mono, uppercase)
.style-section-label--sm   → Versión compacta de etiqueta

.style-card-border         → Borde estándar para cards
.style-card-border--subtle → Borde sutil

.style-badge-base          → Base para badges
.style-badge--light        → Badge claro con background

.style-icon-base           → Base para iconos (28x28px)
.style-icon-base svg       → SVG dentro de icono

.form-error                → Error de formulario (rojo)
.form-text                 → Texto de ayuda en formulario

.autocomplete-results      → Dropdown de autocomplete
.autocomplete-results button
.autocomplete-results-empty

.repuesto-row              → Fila de consumo de repuesto
.repuesto-row--new         → Fila nueva con fondo destacado

PATRONES IMPLEMENTADOS:
========================

✓ Eliminación de inline styles duplicados
  - Antes: Cada componente tenía sus propios estilos inline
  - Ahora: Clases CSS en _base_styles.html (.style-section-label, etc)

✓ Reutilización de iconos SVG
  - Antes: SVG inline en múltiples archivos
  - Ahora: Un único archivo _svg_icon.html con todos los iconos

✓ Eliminación de duplicación en formsets
  - Antes: Las filas del formset se repetían en el form loop y en el template
  - Ahora: Un único partial _repuesto_row.html

✓ Simplificación de filtros
  - Antes: Tres bloques {% if %} completamente diferentes
  - Ahora: Un único template adaptativo que usa {% include %} para selects

✓ Campos de formulario genéricos
  - Antes: Patrón label + input + errores repetido en cada formulario
  - Ahora: _form_field.html reutilizable

CÓMO USAR EN PLANTILLAS PRINCIPALES:
====================================

En cualquier plantilla del modelo mantenimiento que lo necesite:

  {# Incluir estilos una sola vez al inicio (recomendado en la plantilla principal) #}
  {% include "mantenimiento/partials/_base_styles.html" %}

  {# Luego usar los componentes normalmente #}
  <form id="mantenimientoEditForm" method="post" class="row g-3">
    {% csrf_token %}
    
    {% include "mantenimiento/partials/_form_field.html" 
       with field=form.tipo_mantenimiento col_class="col-md-4" 
    %}
    
    {% include "mantenimiento/partials/_form_field.html" 
       with field=form.prioridad col_class="col-md-4" 
    %}
  </form>

  {% include "mantenimiento/partials/_consumo_repuestos_formset.html" %}

BENEFICIOS:
===========

✓ Reducción de líneas de código (~40% menos HTML)
✓ Mantenibilidad: cambios centralizados en un único lugar
✓ Consistencia visual: mismos estilos en toda la app
✓ Reutilización: partials usables en múltiples vistas
✓ Facilidad de testing: componentes más pequeños y aislados
✓ Performance: menos repetición = mejor compresión gzip

EJEMPLOS DE INCLUSIÓN:
======================

# Incluir estilos (UNA SOLA VEZ en la plantilla principal)
{% include "mantenimiento/partials/_base_styles.html" %}

# Renderizar un icono
{% include "mantenimiento/partials/_svg_icon.html" with icon="edit" %}

# Renderizar un badge de estado
{% include "mantenimiento/partials/_badge_estado_registro.html" 
   with estado=obj.estado_registro etiqueta=obj.get_estado_registro_display 
%}

# Renderizar un campo de formulario
{% include "mantenimiento/partials/_form_field.html" 
   with field=form.responsable label="Técnico responsable" col_class="col-md-6" 
%}

# Renderizar filtros adaptativos
{% include "mantenimiento/partials/_filtros.html" 
   with modo="mantenimiento" tipo_choices=tipo_choices estado_choices=estado_choices 
%}

# Renderizar tabla vacía
{% include "mantenimiento/partials/_tabla_empty.html" 
   with colspan=7 empty_mensaje="No hay mantenimientos registrados"
%}

PRÓXIMAS MEJORAS RECOMENDADAS:
==============================

□ Template inheritance base (extend en lugar de solo includes)
□ Macros para componentes más complejos (considera Jinja2)
□ Variantes de temas (light/dark mode en CSS variables)
□ Componentes validados por frontend (JS modules)
□ Documentación visual (styleguide interactivo)
#}
