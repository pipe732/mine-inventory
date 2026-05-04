/* ── Búsqueda en tabla de préstamos ── */
(function () {
  var searchInput = document.getElementById('tbl-search');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      var q = this.value.toLowerCase();
      document.querySelectorAll('#tbl-prestamos tbody tr').forEach(function (tr) {
        tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }
})();

/* ── Modal ver préstamo ── */
function verPrestamo(id, producto, usuario, cantidad, estado, fecha, obs) {
  var estadoBadge = {
    activo:   '<span class="badge-state badge-aprobada">Activo</span>',
    devuelto: '<span class="badge-state badge-pendiente">Devuelto</span>',
    vencido:  '<span class="badge-state badge-rechazada">Vencido</span>'
  };
  var vpProducto = document.getElementById('vp-producto');
  var vpUsuario  = document.getElementById('vp-usuario');
  var vpCantidad = document.getElementById('vp-cantidad');
  var vpEstado   = document.getElementById('vp-estado');
  var vpFecha    = document.getElementById('vp-fecha');
  var vpObs      = document.getElementById('vp-obs');
  var vpLink     = document.getElementById('vp-link');

  if (vpProducto) vpProducto.textContent = producto;
  if (vpUsuario)  vpUsuario.textContent  = usuario;
  if (vpCantidad) vpCantidad.textContent = cantidad;
  if (vpEstado)   vpEstado.innerHTML     = estadoBadge[estado] || estado;
  if (vpFecha)    vpFecha.textContent    = fecha;
  if (vpObs)      vpObs.textContent      = obs || '—';
  if (vpLink)     vpLink.href            = '/prestamos/' + id + '/editar/';

  var modal = document.getElementById('modalVerPrestamo');
  if (modal) new bootstrap.Modal(modal).show();
}

/* ── Modal ver producto ── */
function verProducto(sku, nombre, desc, stock, cat) {
  var vpSku    = document.getElementById('vpd-sku');
  var vpNombre = document.getElementById('vpd-nombre');
  var vpCat    = document.getElementById('vpd-cat');
  var vpStock  = document.getElementById('vpd-stock');
  var vpDesc   = document.getElementById('vpd-desc');
  var vpLink   = document.getElementById('vpd-link');

  if (vpSku)    vpSku.textContent    = sku;
  if (vpNombre) vpNombre.textContent = nombre;
  if (vpCat)    vpCat.textContent    = cat || '—';
  if (vpStock) {
    vpStock.textContent = stock;
    vpStock.style.color = stock === 0 ? 'var(--rust)' : stock < 3 ? '#c4900a' : 'var(--sage)';
  }
  if (vpDesc)  vpDesc.textContent  = desc || '—';
  if (vpLink)  vpLink.href         = '/inventario/' + encodeURIComponent(sku) + '/editar/';

  var modal = document.getElementById('modalVerProducto');
  if (modal) new bootstrap.Modal(modal).show();
}