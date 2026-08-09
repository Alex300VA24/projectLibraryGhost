import { apiFetch } from '../services/api.js';
import { SwalSuccess, SwalError } from '../utils/swal.js';
import { a11yNotify } from '../utils/notify.js';

export function saveProfile(e) {
  e.preventDefault();
  const form = document.getElementById('profile-form');
  const data = new FormData(form);

  apiFetch(form.action, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: data
  }).then(d => {
    if (d.success) {
      if (!a11yNotify('success', 'Cambios guardados', 'Tu perfil se actualizó correctamente.')) SwalSuccess('Cambios guardados', 'Tu perfil se actualizó correctamente.');
    } else {
      if (!a11yNotify('error', 'Error', d.errors ? Object.values(d.errors).join(' ') : 'No se pudieron guardar los cambios.')) Swal.fire({
        icon: 'error', title: 'Error',
        text: d.errors ? Object.values(d.errors).join(' ') : 'No se pudieron guardar los cambios.',
        confirmButtonColor: '#2563eb',
        customClass: { popup: 'swal2-border-radius' }
      });
    }
  }).catch(() => {
    if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.');
  });
  return false;
}

export function changePassword(e) {
  e.preventDefault();
  const form = document.getElementById('password-form');
  const msgDiv = document.getElementById('password-msg');
  const data = new FormData(form);

  apiFetch(form.action, {
    method: 'POST',
    headers: { 'X-CSRFToken': data.get('csrfmiddlewaretoken') },
    body: data
  }).then(d => {
    if (msgDiv) {
      msgDiv.classList.add('hidden');
    }
    if (d.success) {
      if (!a11yNotify('success', 'Contraseña actualizada', 'Tu contraseña se actualizó correctamente.')) SwalSuccess('Contraseña actualizada', 'Tu contraseña se actualizó correctamente.');
      form.reset();
    } else {
      const msgs = [];
      if (d.errors) {
        for (const field in d.errors) {
          msgs.push(d.errors[field].join(' '));
        }
      }
      const text = msgs.length ? msgs.join(' ') : 'Error al cambiar la contraseña.';
      if (!a11yNotify('error', 'Error', text)) SwalError('Error', text);
    }
  }).catch(() => {
    if (msgDiv) {
      msgDiv.classList.add('hidden');
    }
    if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.');
  });
  return false;
}
