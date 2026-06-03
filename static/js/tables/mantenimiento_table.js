/* ═══════════════════════════════════════════
   static/js/tables/mantenimiento_table.js
   DataTable configuration for Mantenimiento
   ═══════════════════════════════════════════ */
$(document).ready(function () {
  $('#mantenimiento-table').DataTable({
    responsive: true,
    dom: '<"row mb-3 align-items-center"<"col-md-6"B><"col-md-6"f>>t<"row mt-3 align-items-center"<"col-md-6"i><"col-md-6"p>>',
    buttons: window.obtenerBotonesDataTable('mantenimiento'),
    language: {
      url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
    },
    order: [],
    columnDefs: [
      { orderable: false, targets: [6, 7] } // Acciones (6) and Historial (7) are not sortable
    ],
    pageLength: 10,
    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, 'Todos']],
    drawCallback: function (settings) {
      // Re-initialize Bootstrap tooltips inside the table after redraw
      var tooltipTriggerList = this.api().table().container().querySelectorAll('[data-bs-toggle="tooltip"]');
      var tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
        return bootstrap.Tooltip.getOrCreateInstance(tooltipTriggerEl);
      });
    }
  });
});
