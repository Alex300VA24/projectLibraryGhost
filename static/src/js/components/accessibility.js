import { apiFetch } from '../services/api.js';
import Alpine from 'alpinejs';

function initAccessibilityStore() {
  Alpine.store('a11y', {
    colorblind: document.body.classList.contains('colorblind-mode'),
    hearing: document.body.classList.contains('hearing-mode'),
    toasts: [],
    toastId: 0,

    toggleColorblind() {
      this.colorblind = !this.colorblind;
      document.body.classList.toggle('colorblind-mode', this.colorblind);
      apiFetch('/cuenta/perfil/accesibilidad/guardar/', {
        method: 'POST',
        body: { colorblind_mode: this.colorblind }
      }).catch(() => {});
      this.showToast('info', 'Modo daltonismo ' + (this.colorblind ? 'activado' : 'desactivado'));
    },

    toggleHearing() {
      this.hearing = !this.hearing;
      document.body.classList.toggle('hearing-mode', this.hearing);
      apiFetch('/cuenta/perfil/accesibilidad/guardar/', {
        method: 'POST',
        body: { hearing_impaired_mode: this.hearing }
      }).catch(() => {});
      this.showToast('info', 'Modo discapacidad auditiva ' + (this.hearing ? 'activado' : 'desactivado'));
    },

    showToast(type, title, description) {
      const id = ++this.toastId;
      this.toasts.push({ id, type, title, description });
      setTimeout(() => this.removeToast(id), 6000);
    },

    removeToast(id) {
      const toast = this.toasts.find(t => t.id === id);
      if (toast) toast.leaving = true;
      setTimeout(() => {
        this.toasts = this.toasts.filter(t => t.id !== id);
      }, 300);
    }
  });
}

export function accessibilityApp() {
  return {
    init() {
      if (!Alpine.store('a11y')) initAccessibilityStore();
      const params = new URLSearchParams(window.location.search);
      const toastType = params.get('toast_type');
      const toastTitle = params.get('toast_title');
      const toastDesc = params.get('toast_desc');
      if (toastType && toastTitle) {
        setTimeout(() => {
          const a11y = Alpine.store('a11y');
          if (a11y?.hearing) {
            a11y.showToast(toastType, toastTitle, toastDesc || '');
          }
        }, 500);
        params.delete('toast_type');
        params.delete('toast_title');
        params.delete('toast_desc');
        const qs = params.toString();
        const url = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
        window.history.replaceState({}, '', url);
      }
    },
    get colorblindMode() { return Alpine.store('a11y')?.colorblind ?? false; },
    get hearingMode() { return Alpine.store('a11y')?.hearing ?? false; },
    get toasts() { return Alpine.store('a11y')?.toasts ?? []; },
    toggleColorblind() { Alpine.store('a11y')?.toggleColorblind(); },
    toggleHearing() { Alpine.store('a11y')?.toggleHearing(); },
    showToast(type, title, desc) { Alpine.store('a11y')?.showToast(type, title, desc); },
    removeToast(id) { Alpine.store('a11y')?.removeToast(id); }
  };
}

export function notifyUser(type, title, description = '') {
  const a11y = Alpine.store('a11y');
  if (a11y?.hearing) {
    a11y.showToast(type, title, description);
    return true;
  }
  return false;
}
