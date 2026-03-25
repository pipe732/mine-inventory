/* ═══════════════════════════════════════════
   devoluciones.js
   Lógica de la vista de devoluciones
═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Chevron filas desplegables ──
  document.querySelectorAll('[data-bs-target^="#detail-"]').forEach(function (btn) {
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

  // ── MINE-106: poblar modal editar con datos de la fila ──
  document.querySelectorAll('.btn-editar').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.getElementById('edit-devolucion-id').value  = this.dataset.id;
      document.getElementById('edit-modal-id').textContent = '#' + this.dataset.id;
      document.getElementById('edit-numero-orden').value   = this.dataset.orden;
      document.getElementById('edit-producto').value       = this.dataset.producto;
      document.getElementById('edit-cantidad').value       = this.dataset.cantidad;
      document.getElementById('edit-motivo').value         = this.dataset.motivo;
      document.getElementById('edit-estado').value         = this.dataset.estado;
    });
  });

});