/* ═══════════════════════════════════════════
   prestamos.js
   Lógica de la vista de préstamos
═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Chevron filas desplegables ──
  document.querySelectorAll('[data-bs-target^="#detail-p-"]').forEach(function (btn) {
    var target = document.querySelector(btn.getAttribute('data-bs-target'));
    if (!target) return;

    target.addEventListener('show.bs.collapse', function () {
      var icon = btn.querySelector('.row-chevron');
      if (icon) icon.style.transform = 'rotate(90deg)';
    });

    target.addEventListener('hide.bs.collapse', function () {
      var icon = btn.querySelector('.row-chevron');
      if (icon) icon.style.transform = 'rotate(0deg)';
    });
  });

  // URL base inyectada desde el template como variable global
  // Se espera: <script>window.PRESTAMO_URL = "{% url 'prestamo' %}";</script>
  var PRESTAMO_URL = window.PRESTAMO_URL || '/prestamos/';

  // ── MINE-128/129/130: Consultar stock y mostrar disponibilidad ──
  (function () {
    var sel       = document.getElementById('id_producto');
    var infoBox   = document.getElementById('stock-info');
    var alertBox  = document.getElementById('stock-alert');
    var label     = document.getElementById('stock-label');
    var submitBtn = document.querySelector('#modalCrearPrestamo [type="submit"]');
    var stockIcon = document.getElementById('stock-icon');

    if (!sel) return;

    function actualizarStock() {
      var opt   = sel.options[sel.selectedIndex];
      var stock = (opt && opt.value) ? parseInt(opt.dataset.stock || '-1', 10) : -1;

      // Resetear
      infoBox.style.display  = 'none';
      alertBox.style.display = 'none';
      if (submitBtn) submitBtn.disabled = false;

      if (stock < 0) return; // sin selección

      if (stock === 0) {
        // MINE-130: Sin stock
        alertBox.style.display = 'flex';
        if (submitBtn) submitBtn.disabled = true;
      } else {
        // MINE-129: Mostrar disponibilidad
        var color = stock <= 3 ? '#d97706' : '#0d9488';
        infoBox.style.display    = 'flex';
        infoBox.style.background = stock <= 3 ? 'rgba(245,158,11,.08)' : 'rgba(45,212,191,.08)';
        infoBox.style.border     = stock <= 3 ? '1px solid rgba(217,119,6,.25)' : '1px solid rgba(45,212,191,.25)';
        infoBox.style.color      = color;
        if (stockIcon) stockIcon.style.stroke = color;
        label.textContent = stock <= 3
          ? 'Stock bajo: ' + stock + ' unidad' + (stock === 1 ? '' : 'es') + ' disponible' + (stock === 1 ? '' : 's')
          : 'Disponible: ' + stock + ' unidades en stock';
      }
    }

    sel.addEventListener('change', actualizarStock);

    // Ejecutar al abrir el modal si ya hay un producto seleccionado
    var modalCrear = document.getElementById('modalCrearPrestamo');
    if (modalCrear) {
      modalCrear.addEventListener('shown.bs.modal', actualizarStock);
    }
  })();

  // ── Modal Editar (MINE-123 / MINE-124) ──
  var modalEditar = document.getElementById('modalEditarPrestamo');
  if (modalEditar) {
    modalEditar.addEventListener('show.bs.modal', function (e) {
      var btn = e.relatedTarget;
      document.getElementById('edit_pk').value             = btn.dataset.pk;
      document.getElementById('edit_observaciones').value  = btn.dataset.observaciones || '';
      var selEstado   = document.getElementById('edit_estado');
      var selUsuario  = document.getElementById('edit_usuario');
      if (selEstado)  selEstado.value  = btn.dataset.estado   || 'activo';
      if (selUsuario) selUsuario.value = btn.dataset.usuario  || '';
      document.getElementById('formEditarPrestamo').action = PRESTAMO_URL;
    });
  }

  // ── Modal Cancelar (MINE-125 / MINE-126) ──
  var modalCancelar = document.getElementById('modalCancelarPrestamo');
  if (modalCancelar) {
    modalCancelar.addEventListener('show.bs.modal', function (e) {
      var btn = e.relatedTarget;
      document.getElementById('cancelar_pk').value                    = btn.dataset.pk;
      document.getElementById('cancelar_usuario_label').textContent   = btn.dataset.usuario;
      e.currentTarget.querySelector('form').action = PRESTAMO_URL;
    });
  }

  // ── Modal Eliminar (MINE-127) ──
  var modalEliminar = document.getElementById('modalEliminarPrestamo');
  if (modalEliminar) {
    modalEliminar.addEventListener('show.bs.modal', function (e) {
      var btn = e.relatedTarget;
      document.getElementById('eliminar_pk').value                    = btn.dataset.pk;
      document.getElementById('eliminar_usuario_label').textContent   = btn.dataset.usuario;
      e.currentTarget.querySelector('form').action = PRESTAMO_URL;
    });
  }

});