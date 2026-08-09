import { apiFetch } from '../services/api.js';
import { API } from '../services/urls.js';
import { a11yNotify } from '../utils/notify.js';

export function orderPage() {
  return {
    showConfirmModal: false,
    confirmTitle: '',
    confirmMessage: '',
    confirmIcon: 'fa-solid fa-triangle-exclamation',
    confirmIconBg: 'bg-red-100',
    confirmIconColor: 'text-red-500',
    confirmButtonText: 'Confirmar',
    confirmButtonClass: 'btn-danger flex-1 py-3 text-sm font-bold',
    confirmAction: '',
    confirmData: null,

    confirmCancel(orderId) {
      this.confirmTitle = '¿Cancelar este pedido?';
      this.confirmMessage = 'Esta acción no se puede deshacer.';
      this.confirmIcon = 'fa-solid fa-triangle-exclamation';
      this.confirmIconBg = 'bg-red-100';
      this.confirmIconColor = 'text-red-500';
      this.confirmButtonText = 'Sí, cancelar';
      this.confirmButtonClass = 'btn-danger flex-1 py-3 text-sm font-bold';
      this.confirmAction = 'cancel-order';
      this.confirmData = orderId;
      this.showConfirmModal = true;
    },

    handleConfirm() {
      const orderId = this.confirmData;
      this.showConfirmModal = false;

      const csrfMeta = document.querySelector('meta[name="csrf-token"]');
      const csrf = csrfMeta ? csrfMeta.content : '';
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = API.ORDER_CANCEL(orderId);
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = csrf;
      form.appendChild(csrfInput);
      document.body.appendChild(form);
      a11yNotify('warning', 'Pedido cancelado');
      form.submit();
    }
  };
}
