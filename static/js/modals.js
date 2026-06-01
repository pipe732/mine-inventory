document.addEventListener('DOMContentLoaded', function () {
  var modals = document.querySelectorAll('.modal');

  modals.forEach(function (modal) {
    modal.addEventListener('hidden.bs.modal', function () {
      var form = modal.querySelector('form');

      if (form) {
        form.reset();
      }

      modal.querySelectorAll('.invalid-feedback, .alert-danger').forEach(function (node) {
        node.remove();
      });

      modal.querySelectorAll('.is-invalid').forEach(function (node) {
        node.classList.remove('is-invalid');
      });
    });

    if (modal.dataset.hasErrors === 'true' && window.bootstrap && bootstrap.Modal) {
      bootstrap.Modal.getOrCreateInstance(modal).show();
    }
  });
});
