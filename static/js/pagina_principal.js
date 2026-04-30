/* ── Búsqueda en tabla de préstamos ── */
document.getElementById('tbl-search').addEventListener('input', function () {
  var q = this.value.toLowerCase();
  document.querySelectorAll('#tbl-prestamos tbody tr').forEach(function (tr) {
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
});

/* ── Modal ver préstamo ── */
function verPrestamo(id, producto, usuario, cantidad, estado, fecha, obs) {
  var estadoBadge = {
    activo:   '<span class="badge-state badge-aprobada">Activo</span>',
    devuelto: '<span class="badge-state badge-pendiente">Devuelto</span>',
    vencido:  '<span class="badge-state badge-rechazada">Vencido</span>'
  };
  document.getElementById('vp-producto').textContent = producto;
  document.getElementById('vp-usuario').textContent  = usuario;
  document.getElementById('vp-cantidad').textContent = cantidad;
  document.getElementById('vp-estado').innerHTML     = estadoBadge[estado] || estado;
  document.getElementById('vp-fecha').textContent    = fecha;
  document.getElementById('vp-obs').textContent      = obs || '—';
  document.getElementById('vp-link').href            = '/prestamos/' + id + '/editar/';
  new bootstrap.Modal(document.getElementById('modalVerPrestamo')).show();
}

/* ── Modal ver producto ── */
function verProducto(sku, nombre, desc, stock, cat) {
  document.getElementById('vpd-sku').textContent    = sku;
  document.getElementById('vpd-nombre').textContent = nombre;
  document.getElementById('vpd-cat').textContent    = cat || '—';
  var el = document.getElementById('vpd-stock');
  el.textContent = stock;
  el.style.color = stock === 0 ? 'var(--rust)' : stock < 3 ? '#c4900a' : 'var(--sage)';
  document.getElementById('vpd-desc').textContent   = desc || '—';
  document.getElementById('vpd-link').href          = '/inventario/' + encodeURIComponent(sku) + '/editar/';
  new bootstrap.Modal(document.getElementById('modalVerProducto')).show();
}