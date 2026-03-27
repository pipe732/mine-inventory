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

});