(function () {

  /* ══════════════════════════════════════════
     ESTADO inicial desde localStorage
  ══════════════════════════════════════════ */
  var fontSize  = parseInt(localStorage.getItem('acc_fs') || '100');
  var contrast  = localStorage.getItem('acc_contrast') === 'true';
  var darkMode  = localStorage.getItem('acc_dark')     === 'true';
  var lightMode = localStorage.getItem('acc_light')    === 'true';

  document.documentElement.style.fontSize = fontSize + '%';

  /* ══════════════════════════════════════════
     INYECTAR estilos CSS helper en <head>
     Usa aside[data-acc-dark] para máxima
     especificidad sobre las clases de Bootstrap
  ══════════════════════════════════════════ */
  var helperStyle = document.createElement('style');
  helperStyle.id  = 'acc-helper-styles';
  helperStyle.textContent = [
    'aside[data-acc-dark] { background:#fff !important; border-right:1px solid rgba(27,32,33,.14) !important; }',
    'aside[data-acc-dark]::-webkit-scrollbar-thumb { background:rgba(27,32,33,.15) !important; }',
    'aside[data-acc-dark] .aside-header   { color:rgba(27,32,33,.4) !important; border-bottom-color:rgba(27,32,33,.08) !important; }',
    'aside[data-acc-dark] .aside-brand-name { color:#1B2021 !important; }',
    'aside[data-acc-dark] .aside-brand-sub  { color:rgba(27,32,33,.4) !important; }',
    'aside[data-acc-dark] hr { border-color:rgba(27,32,33,.1) !important; opacity:1 !important; }',
    'aside[data-acc-dark] .bi-chevron-down { color:#1B2021 !important; opacity:.25 !important; }',
    'aside[data-acc-dark] .nav-icon { opacity:.42; }',
    /* clases helper que reemplazan text-white-50 y text-white de Bootstrap */
    'aside[data-acc-dark] ._al { color:rgba(27,32,33,.58) !important; }',
    'aside[data-acc-dark] ._al:hover { color:#1B2021 !important; background:rgba(27,32,33,.06) !important; }',
    'aside[data-acc-dark] ._al:hover .nav-icon { opacity:.85; }',
    'aside[data-acc-dark] ._aa { color:#1B2021 !important; }',
    'aside[data-acc-dark] ._ab { background:rgba(27,32,33,.08) !important; }',
    /* nav-bottom */
    'aside[data-acc-dark] .nav-bottom { border-top-color:rgba(27,32,33,.1) !important; }',
    /* Submenús colores especiales */
    'aside[data-acc-dark] .text-info    { color:rgba(9,77,146,.75) !important; }',
    'aside[data-acc-dark] .text-warning { color:rgba(130,85,10,.85) !important; }',
    /* Dropdown usuario */
    'aside[data-acc-dark] .dropdown-menu       { background:#fff !important; border-color:rgba(27,32,33,.1) !important; }',
    'aside[data-acc-dark] .dropdown-item       { color:rgba(27,32,33,.75) !important; }',
    'aside[data-acc-dark] .dropdown-item:hover { background:rgba(27,32,33,.05) !important; color:#1B2021 !important; }',
    'aside[data-acc-dark] .dropdown-item.text-danger { color:#98473E !important; }',
    'aside[data-acc-dark] .dropdown-divider    { border-color:rgba(27,32,33,.08) !important; }',
    'aside[data-acc-dark] .dropdown-item-text  { color:rgba(27,32,33,.35) !important; }',
  ].join('\n');
  document.head.appendChild(helperStyle);

  /* ══════════════════════════════════════════
     ASIDE: aplicar / quitar tema blanco
  ══════════════════════════════════════════ */
  function applyAsideDark() {
    var aside = document.querySelector('aside');
    if (!aside) return;

    /* Marca que activa todos los selectores CSS helper */
    aside.setAttribute('data-acc-dark', '1');

    /* Botón usuario — style inline con rgba(255…) */
    var btn = aside.querySelector('.dropup > button');
    if (btn) {
      btn.style.cssText = btn.style.cssText
        .replace(/background:[^;]+;?/gi, '')
        .replace(/border:[^;]+;?/gi, '')
        .replace(/color:[^;]+;?/gi, '');
      btn.style.setProperty('background', 'rgba(27,32,33,.06)', 'important');
      btn.style.setProperty('border',     '1px solid rgba(27,32,33,.13)', 'important');
      btn.style.setProperty('color',      'rgba(27,32,33,.78)', 'important');
    }

    /* Badge "pronto" — style inline con rgba(255…) */
    aside.querySelectorAll('.badge[style]').forEach(function (el) {
      el.style.setProperty('background', 'rgba(27,32,33,.08)', 'important');
      el.style.setProperty('color',      'rgba(27,32,33,.45)', 'important');
    });

    /* Etiquetas de sección — style inline color rgba(255…) */
    aside.querySelectorAll('span.text-uppercase[style]').forEach(function (el) {
      el.style.setProperty('color', 'rgba(27,32,33,.38)', 'important');
    });

    /* Reemplazar clases Bootstrap */
    aside.querySelectorAll('.text-white-50').forEach(function (el) {
      el.classList.replace('text-white-50', '_al');
    });
    aside.querySelectorAll('.text-white').forEach(function (el) {
      el.classList.replace('text-white', '_aa');
    });
    aside.querySelectorAll('.bg-white.bg-opacity-10').forEach(function (el) {
      el.classList.remove('bg-white', 'bg-opacity-10');
      el.classList.add('_ab');
    });
  }

  function resetAsideDark() {
    var aside = document.querySelector('aside');
    if (!aside) return;

    aside.removeAttribute('data-acc-dark');

    var btn = aside.querySelector('.dropup > button');
    if (btn) {
      btn.style.setProperty('background', 'rgba(255,255,255,.05)', 'important');
      btn.style.setProperty('border',     '1px solid rgba(255,255,255,.07)', 'important');
      btn.style.setProperty('color',      'rgba(239,236,202,.85)', 'important');
    }

    aside.querySelectorAll('.badge[style]').forEach(function (el) {
      el.style.setProperty('background', 'rgba(255,255,255,.1)', 'important');
      el.style.setProperty('color',      'rgba(255,255,255,.5)', 'important');
    });

    aside.querySelectorAll('span.text-uppercase[style]').forEach(function (el) {
      el.style.setProperty('color', 'rgba(255,255,255,.25)', 'important');
    });

    aside.querySelectorAll('._al').forEach(function (el) {
      el.classList.replace('_al', 'text-white-50');
    });
    aside.querySelectorAll('._aa').forEach(function (el) {
      el.classList.replace('_aa', 'text-white');
    });
    aside.querySelectorAll('._ab').forEach(function (el) {
      el.classList.remove('_ab');
      el.classList.add('bg-white', 'bg-opacity-10');
    });
  }

  /* ══════════════════════════════════════════
     APLICAR ESTADO GUARDADO
     (script está al final del body → DOM listo)
  ══════════════════════════════════════════ */
  if (contrast)  document.body.classList.add('high-contrast');
  if (lightMode) document.body.classList.add('light-mode');
  if (darkMode) {
    document.body.classList.add('dark-mode');
    applyAsideDark();
  }

  /* ══════════════════════════════════════════
     SYNC botones
  ══════════════════════════════════════════ */
  function syncButtons() {
    var c = document.getElementById('acc-btn-contrast');
    var d = document.getElementById('acc-btn-dark');
    var l = document.getElementById('acc-btn-light');
    if (c) c.classList.toggle('acc-active', contrast);
    if (d) d.classList.toggle('acc-active', darkMode);
    if (l) l.classList.toggle('acc-active', lightMode);
  }

  /* ══════════════════════════════════════════
     REPINTAR panel para recalcular CSS vars
     (necesario cuando cambia body.dark-mode)
  ══════════════════════════════════════════ */
  function repaintPanel() {
    var p = document.getElementById('acc-panel');
    if (!p || !p.classList.contains('acc-open')) return;
    p.style.display = 'none';
    p.offsetHeight; // force reflow
    p.style.display = '';
    p.classList.add('acc-open');
  }

  /* ══════════════════════════════════════════
     EVENTOS del widget
  ══════════════════════════════════════════ */
  var toggle = document.getElementById('acc-toggle');
  var panel  = document.getElementById('acc-panel');

  if (toggle && panel) {

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      panel.classList.toggle('acc-open');
    });

    document.addEventListener('click', function (e) {
      var widget = document.getElementById('acc-widget');
      if (widget && !widget.contains(e.target)) panel.classList.remove('acc-open');
    });

    document.getElementById('acc-btn-contrast').addEventListener('click', function () {
      contrast = !contrast;
      document.body.classList.toggle('high-contrast', contrast);
      localStorage.setItem('acc_contrast', contrast);
      syncButtons();
    });

    document.getElementById('acc-btn-dark').addEventListener('click', function () {
      darkMode = !darkMode;
      if (darkMode) {
        lightMode = false;
        document.body.classList.remove('light-mode');
        localStorage.setItem('acc_light', 'false');
        applyAsideDark();
      } else {
        resetAsideDark();
      }
      document.body.classList.toggle('dark-mode', darkMode);
      localStorage.setItem('acc_dark', darkMode);
      syncButtons();
      repaintPanel();
    });

    document.getElementById('acc-btn-light').addEventListener('click', function () {
      lightMode = !lightMode;
      if (lightMode) {
        darkMode = false;
        document.body.classList.remove('dark-mode');
        localStorage.setItem('acc_dark', 'false');
        resetAsideDark();
      }
      document.body.classList.toggle('light-mode', lightMode);
      localStorage.setItem('acc_light', lightMode);
      syncButtons();
      repaintPanel();
    });

    document.getElementById('acc-btn-plus').addEventListener('click', function () {
      if (fontSize >= 140) return;
      fontSize += 10;
      document.documentElement.style.fontSize = fontSize + '%';
      localStorage.setItem('acc_fs', fontSize);
    });

    document.getElementById('acc-btn-minus').addEventListener('click', function () {
      if (fontSize <= 70) return;
      fontSize -= 10;
      document.documentElement.style.fontSize = fontSize + '%';
      localStorage.setItem('acc_fs', fontSize);
    });

    document.getElementById('acc-btn-reset').addEventListener('click', function () {
      fontSize = 100; contrast = false; darkMode = false; lightMode = false;
      document.body.classList.remove('high-contrast', 'dark-mode', 'light-mode');
      document.documentElement.style.fontSize = '100%';
      resetAsideDark();
      localStorage.removeItem('acc_fs');
      localStorage.removeItem('acc_contrast');
      localStorage.removeItem('acc_dark');
      localStorage.removeItem('acc_light');
      syncButtons();
    });

    syncButtons();
  }

})();