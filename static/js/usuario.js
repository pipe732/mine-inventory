// LOGIN

const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', function (e) {
    const doc  = document.getElementById('documento').value.trim();
    const pwd  = document.getElementById('password').value.trim();
    const area = document.getElementById('msg-area');
    area.innerHTML = '';

    if (!doc || !pwd) {
      e.preventDefault();
      area.innerHTML = `
        <div class="alert alert-danger d-flex align-items-center gap-2 py-2 px-3 small mb-3">
          <i class="bi bi-exclamation-circle-fill"></i>
          Por favor ingresa tu documento y contraseña.
        </div>`;
    }
  });

  const docInput = document.getElementById('documento');
  if (docInput) {
    docInput.addEventListener('input', function () {
      this.value = this.value.replace(/[^0-9]/g, '');
    });
  }
}


// OLVIDO DE CONTRASEÑA

const recForm = document.getElementById('recForm');
if (recForm) {
  recForm.addEventListener('submit', function (e) {
    const email = document.getElementById('email').value.trim();
    const area  = document.getElementById('msg-area');
    area.innerHTML = '';

    const error = msg => {
      e.preventDefault();
      area.innerHTML = `
        <div class="alert alert-danger d-flex align-items-center gap-2 py-2 px-3 small mb-3">
          <i class="bi bi-exclamation-circle-fill"></i>${msg}
        </div>`;
    };

    if (!email) return error('Por favor ingresa tu correo electrónico.');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return error('Ingresa un correo electrónico válido.');
  });
}


// REGISTRO

const regForm = document.getElementById('regForm');
if (regForm) {
  regForm.addEventListener('submit', function (e) {
    const nombre = document.getElementById('username').value.trim();
    const email  = document.getElementById('email').value.trim();
    const doc    = document.getElementById('documento').value.trim();
    const p1     = document.getElementById('password1').value;
    const p2     = document.getElementById('password2').value;
    const area   = document.getElementById('msg-area');
    area.innerHTML = '';

    const error = msg => {
      e.preventDefault();
      area.innerHTML = `
        <div class="alert alert-danger d-flex align-items-center gap-2 py-2 px-3 small mb-3">
          <i class="bi bi-exclamation-circle-fill"></i>${msg}
        </div>`;
    };

    if (!nombre || !email || !doc || !p1 || !p2) return error('Por favor completa todos los campos.');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))  return error('Ingresa un correo electrónico válido.');
    if (p1.length < 8)  return error('La contraseña debe tener mínimo 8 caracteres.');
    if (p1 !== p2)      return error('Las contraseñas no coinciden.');
  });

  const docInput = document.getElementById('documento');
  if (docInput) {
    docInput.addEventListener('input', function () {
      this.value = this.value.replace(/[^0-9]/g, '');
    });
  }
}