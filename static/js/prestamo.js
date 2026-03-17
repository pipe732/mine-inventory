  document.getElementById('btnAgregarFila').addEventListener('click', function () {
    const tbody = document.getElementById('bodyDetalles');
    const fila  = document.querySelector('.fila-detalle').cloneNode(true);
    fila.querySelectorAll('input').forEach(i => {
      i.value = (i.type === 'number' && i.name.includes('cantidad')) ? 1 : '';
    });
    fila.querySelector('.btn-quitar').disabled = false;
    tbody.appendChild(fila);
    actualizarBotones();
  });

  document.getElementById('bodyDetalles').addEventListener('click', function (e) {
    if (e.target.closest('.btn-quitar')) {
      const filas = document.querySelectorAll('.fila-detalle');
      if (filas.length > 1) {
        e.target.closest('.fila-detalle').remove();
        actualizarBotones();
      }
    }
  });

  function actualizarBotones() {
    const filas = document.querySelectorAll('.fila-detalle');
    filas.forEach(f => { f.querySelector('.btn-quitar').disabled = filas.length === 1; });
  }

  function confirmarEliminar(url) {
    document.getElementById('formEliminar').action = url;
    new bootstrap.Modal(document.getElementById('modalEliminar')).show();
  }