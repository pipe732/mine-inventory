/* ═══════════════════════════════════════════
   static/js/tables/devoluciones_table.js
   DataTable, Details & Actions for Devoluciones
  ═══════════════════════════════════════════ */
$(document).ready(function () {
  var childRows = {};

  // Extraer y remover las filas de detalle antes de inicializar la tabla
  $('#devoluciones-table tbody tr.detail-row').each(function () {
    var id = $(this).attr('id');
    childRows[id] = $(this).html();
    $(this).remove();
  });

  // Inicializar DataTable
  var table = $('#devoluciones-table').DataTable({
    responsive: true,
    dom: '<"row mb-3 align-items-center"<"col-md-6"B><"col-md-6"f>>t<"row mt-3 align-items-center"<"col-md-6"i><"col-md-6"p>>',
    buttons: window.obtenerBotonesDataTable('devoluciones'),
    language: {
      url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
    },
    order: [],
    columnDefs: [
      { orderable: false, targets: [0, 4, 6] } // expand (0), items count (4), actions (6) no ordenables
    ],
    pageLength: 10,
    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, 'Todos']],
    drawCallback: function (settings) {
      // Re-inicializar tooltips dentro de la tabla
      var tooltipTriggerList = this.api().table().container().querySelectorAll('[data-bs-toggle="tooltip"]');
      var tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
        return bootstrap.Tooltip.getOrCreateInstance(tooltipTriggerEl);
      });
    }
  });

  // Manejar clic en el botón de expandir
  $('#devoluciones-table').on('click', '.btn-toggle-details', function (e) {
    e.preventDefault();
    var btn = $(this);
    var targetId = btn.attr('data-target-detail');
    var tr = btn.closest('tr');
    var row = table.row(tr);

    if (row.child.isShown()) {
      row.child.hide();
      tr.removeClass('shown');
      btn.find('.row-chevron').css('transform', 'rotate(0deg)');
    } else {
      var content = childRows[targetId];
      row.child(content).show();
      row.child().find('td').attr('colspan', 7).css('padding', '0');
      tr.addClass('shown');
      btn.find('.row-chevron').css('transform', 'rotate(90deg)');
    }
  });

  // Manejar clic delegados en el botón de Aceptar devolución (para que funcione con paginación/búsqueda de DataTable)
  $('#devoluciones-table').on('click', '.btn-aceptar-click', function (e) {
    e.preventDefault();
    var btn = $(this);
    var pk = btn.attr('data-pk');
    var prestamoPk = btn.attr('data-prestamo-pk');
    var usuario = btn.attr('data-usuario');
    abrirAceptar(pk, prestamoPk, usuario);
  });

  // Manejar clic delegados en el botón de Rechazar devolución (para que funcione con paginación/búsqueda de DataTable)
  $('#devoluciones-table').on('click', '.btn-rechazar-click', function (e) {
    e.preventDefault();
    var btn = $(this);
    var pk = btn.attr('data-pk');
    var prestamoPk = btn.attr('data-prestamo-pk');
    var usuario = btn.attr('data-usuario');
    abrirRechazar(pk, prestamoPk, usuario);
  });
});
