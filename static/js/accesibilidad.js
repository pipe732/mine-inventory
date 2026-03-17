(function () {
  var fontSize  = parseInt(localStorage.getItem('acc_fs') || '100');
  var contrast  = localStorage.getItem('acc_contrast') === 'true';
  var darkMode  = localStorage.getItem('acc_dark')     === 'true';
  var lightMode = localStorage.getItem('acc_light')    === 'true';

  /* Aplicar estado guardado inmediatamente */
  document.documentElement.style.fontSize = fontSize + '%';
  if (contrast)  document.body.classList.add('high-contrast');
  if (darkMode)  document.body.classList.add('dark-mode');
  if (lightMode) document.body.classList.add('light-mode');

  function syncButtons() {
    var c = document.getElementById('acc-btn-contrast');
    var d = document.getElementById('acc-btn-dark');
    var l = document.getElementById('acc-btn-light');
    if (c) c.classList.toggle('acc-active', contrast);
    if (d) d.classList.toggle('acc-active', darkMode);
    if (l) l.classList.toggle('acc-active', lightMode);
  }

  function init() {
    var toggle = document.getElementById('acc-toggle');
    var panel  = document.getElementById('acc-panel');

    if (!toggle || !panel) return;

    /* Abrir / cerrar panel */
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      panel.classList.toggle('acc-open');
    });

    /* Cerrar al clic fuera */
    document.addEventListener('click', function (e) {
      var widget = document.getElementById('acc-widget');
      if (widget && !widget.contains(e.target)) {
        panel.classList.remove('acc-open');
      }
    });

    /* Contraste */
    document.getElementById('acc-btn-contrast').addEventListener('click', function () {
      contrast = !contrast;
      document.body.classList.toggle('high-contrast', contrast);
      localStorage.setItem('acc_contrast', contrast);
      syncButtons();
    });

    /* Modo oscuro */
    document.getElementById('acc-btn-dark').addEventListener('click', function () {
      darkMode = !darkMode;
      if (darkMode) {
        lightMode = false;
        document.body.classList.remove('light-mode');
        localStorage.setItem('acc_light', 'false');
      }
      document.body.classList.toggle('dark-mode', darkMode);
      localStorage.setItem('acc_dark', darkMode);
      syncButtons();
    });

    /* Modo claro */
    document.getElementById('acc-btn-light').addEventListener('click', function () {
      lightMode = !lightMode;
      if (lightMode) {
        darkMode = false;
        document.body.classList.remove('dark-mode');
        localStorage.setItem('acc_dark', 'false');
      }
      document.body.classList.toggle('light-mode', lightMode);
      localStorage.setItem('acc_light', lightMode);
      syncButtons();
    });

    /* Aumentar letra */
    document.getElementById('acc-btn-plus').addEventListener('click', function () {
      if (fontSize >= 140) return;
      fontSize += 10;
      document.documentElement.style.fontSize = fontSize + '%';
      localStorage.setItem('acc_fs', fontSize);
    });

    /* Reducir letra */
    document.getElementById('acc-btn-minus').addEventListener('click', function () {
      if (fontSize <= 70) return;
      fontSize -= 10;
      document.documentElement.style.fontSize = fontSize + '%';
      localStorage.setItem('acc_fs', fontSize);
    });

    /* Restablecer */
    document.getElementById('acc-btn-reset').addEventListener('click', function () {
      fontSize = 100; contrast = false; darkMode = false; lightMode = false;
      document.body.classList.remove('high-contrast', 'dark-mode', 'light-mode');
      document.documentElement.style.fontSize = '100%';
      localStorage.removeItem('acc_fs');
      localStorage.removeItem('acc_contrast');
      localStorage.removeItem('acc_dark');
      localStorage.removeItem('acc_light');
      syncButtons();
    });

    syncButtons();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();