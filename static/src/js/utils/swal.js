import Swal from 'sweetalert2';

const CONFIRM_BLUE = '#2563eb';
const CANCEL_GRAY = '#78716c';
const DANGER_RED = '#ef4444';
const COMMON = {
  confirmButtonText: 'Aceptar',
  customClass: { popup: 'swal2-border-radius' }
};

export { CONFIRM_BLUE, DANGER_RED, CANCEL_GRAY };

export function SwalSuccess(title, text = '') {
  return Swal.fire({ ...COMMON, icon: 'success', title, text, confirmButtonColor: CONFIRM_BLUE });
}

export function SwalError(title, text = '') {
  return Swal.fire({ ...COMMON, icon: 'error', title, text, confirmButtonColor: DANGER_RED });
}

export function SwalToast(icon, title) {
  return Swal.fire({ icon, title, toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 });
}

export function SwalAddToCart(productName = '') {
  return Swal.fire({
    icon: 'success',
    title: productName ? `¡${productName} agregado!` : '¡Agregado al carrito!',
    showConfirmButton: false,
    timer: 1600,
    position: 'center',
    backdrop: 'rgba(30,58,138,0.35)',
    width: 380,
    padding: '1.8rem 1.5rem',
    customClass: { popup: 'swal2-border-radius' }
  });
}

export function SwalWarning(title, text = '') {
  return Swal.fire({ ...COMMON, icon: 'warning', title, text, confirmButtonColor: CONFIRM_BLUE });
}

export function SwalConfirm(title, text = '', onConfirm, options = {}) {
  return Swal.fire({
    ...COMMON, title, text, icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: options.confirmColor || CONFIRM_BLUE,
    cancelButtonColor: CANCEL_GRAY,
    confirmButtonText: options.confirmText || 'Confirmar',
    cancelButtonText: 'Cancelar',
  }).then(result => { if (result.isConfirmed) onConfirm(); });
}
