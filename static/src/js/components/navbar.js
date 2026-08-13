import { getCsrf, apiFetch } from '../services/api.js';
import { SwalError, SwalWarning } from '../utils/swal.js';
import { statusDisplay, isOrderCancellable } from '../utils/status.js';
import { API } from '../services/urls.js';
import { a11yNotify } from '../utils/notify.js';

const NOTIF_POLL_INTERVAL = 15000;

export function navbarApp() {
  return {
    mobileMenuOpen: false,
    openCart: false,
    openOrders: false,
    openPayment: false,
    showBoleta: false,
    showAuthModal: false,
    showConfirmModal: false,
    showNotifPanel: false,
    notifCount: 0,
    notifList: [],
    notifPollId: null,
    notifLoading: false,
    confirmTitle: '',
    confirmMessage: '',
    confirmIcon: 'fa-solid fa-triangle-exclamation',
    confirmIconBg: 'bg-red-100',
    confirmIconColor: 'text-red-500',
    confirmButtonText: 'Confirmar',
    confirmButtonClass: 'btn-danger flex-1 py-3 text-sm font-bold',
    confirmAction: '',
    confirmData: null,
    loginUrl: '',
    cartItems: [],
    cartTotal: 0,
    cartCount: 0,
    orders: [],
    orderDetail: null,
    openOrderDetail: false,
    paymentMethod: '',
    montoRecibido: 0,
    boletaData: null,

    initNavbar() {
      const params = new URLSearchParams(window.location.search);
      if (params.get('modal') === 'carrito') {
        this.openCart = true;
        this.loadCart();
      } else if (params.get('modal') === 'pedidos') {
        this.openOrders = true;
      }
      if (params.get('modal')) {
        const url = new URL(window.location);
        url.searchParams.delete('modal');
        window.history.replaceState({}, '', url);
      }
      this.loginUrl = document.querySelector('meta[name="login-url"]')?.content || API.LOGIN;
      window.addEventListener('ym:cartUpdated', e => {
        if (e.detail && typeof e.detail.count !== 'undefined') {
          this.cartCount = e.detail.count;
        }
        if (e.detail && e.detail.showCart) {
          this.openCart = true;
          this.loadCart();
        }
      });
      apiFetch(API.CART_DATA).then(d => {
        if (d.success) { this.cartCount = d.count || d.items.length; }
      }).catch(() => {});
      const isLoggedIn = document.querySelector('meta[name="user-is-authenticated"]')?.content === 'true';
      if (isLoggedIn) {
        this.startNotifPolling();
      }
    },

    loadNotif() {
      this.notifLoading = true;
      apiFetch(API.DASHBOARD_NOTIFICACIONES).then(d => {
        if (d.success) {
          this.notifList = d.notifications;
        }
      }).catch(() => {}).finally(() => { this.notifLoading = false; });
    },

    countNotif() {
      apiFetch(API.DASHBOARD_NOTIFICACIONES_CONTADOR).then(d => {
        if (d.success) this.notifCount = d.count;
      }).catch(() => {});
    },

    toggleNotifPanel() {
      this.showNotifPanel = !this.showNotifPanel;
      if (this.showNotifPanel) {
        this.loadNotif();
      }
    },

    marcarLeidas() {
      apiFetch(API.DASHBOARD_NOTIFICACIONES_LEER_TODAS, { method: 'POST' }).then(d => {
        if (d.success) {
          this.notifCount = 0;
          this.notifList.forEach(n => n.is_read = true);
          a11yNotify('success', 'Notificaciones marcadas como leídas');
        }
      }).catch(() => {});
    },

    marcarLeida(notification) {
      apiFetch(API.DASHBOARD_NOTIFICACIONES_LEER(notification.id), { method: 'POST' }).then(d => {
        if (d.success) {
          notification.is_read = true;
          this.notifCount = Math.max(0, this.notifCount - 1);
          a11yNotify('success', 'Notificación marcada como leída');
        }
      }).catch(() => {});
    },

    startNotifPolling() {
      this.countNotif();
      this.notifPollId = setInterval(() => { this.countNotif(); }, NOTIF_POLL_INTERVAL);
    },

    loadCart() {
      apiFetch(API.CART_DATA).then(d => {
        if (d.success) {
          this.cartItems = d.items;
          this.cartTotal = d.total;
          this.cartCount = d.count || d.items.length;
        }
      }).catch(() => { this.cartItems = []; this.cartTotal = 0; this.cartCount = 0; });
    },

    updateCartItem(itemId, qty) {
      apiFetch(API.CART_UPDATE(itemId), {
        method: 'POST',
        body: { quantity: qty }
      }).then(d => {
        if (d.success) {
          if (qty <= 0) {
            this.cartItems = this.cartItems.filter(i => i.id !== itemId);
            a11yNotify('info', 'Producto eliminado del carrito');
          } else {
            const item = this.cartItems.find(i => i.id === itemId);
            if (item) {
              item.quantity = qty;
              item.subtotal = parseFloat(d.subtotal);
            }
            a11yNotify('info', 'Cantidad actualizada');
          }
          this.cartTotal = parseFloat(d.cart_total);
          this.cartCount = d.cart_count;
        }
      });
    },

    removeCartItem(itemId) {
      this.confirmTitle = '¿Quitar producto?';
      this.confirmMessage = '¿Estás seguro de quitar este producto del carrito?';
      this.confirmIcon = 'fa-solid fa-circle-question';
      this.confirmIconBg = 'bg-blue-100';
      this.confirmIconColor = 'text-blue-500';
      this.confirmButtonText = 'Sí, quitar';
      this.confirmButtonClass = 'btn-danger flex-1 py-3 text-sm font-bold';
      this.confirmAction = 'remove-cart-item';
      this.confirmData = itemId;
      this.showConfirmModal = true;
    },

    emptyCart() {
      this.confirmTitle = '¿Vaciar carrito?';
      this.confirmMessage = 'Se quitarán todos los productos del carrito.';
      this.confirmIcon = 'fa-solid fa-circle-question';
      this.confirmIconBg = 'bg-blue-100';
      this.confirmIconColor = 'text-blue-500';
      this.confirmButtonText = 'Sí, quitar todo';
      this.confirmButtonClass = 'btn-danger flex-1 py-3 text-sm font-bold';
      this.confirmAction = 'empty-cart';
      this.confirmData = null;
      this.showConfirmModal = true;
    },

    handleConfirm() {
      const action = this.confirmAction;
      const data = this.confirmData;
      this.showConfirmModal = false;

      if (action === 'remove-cart-item') {
        apiFetch(API.CART_REMOVE(data), { method: 'POST', body: {} }).then(d => {
          this.cartItems = this.cartItems.filter(i => i.id !== data);
          if (d.success) {
            this.cartTotal = parseFloat(d.cart_total);
            this.cartCount = d.cart_count;
            a11yNotify('warning', 'Producto eliminado del carrito');
          }
        });
      } else if (action === 'empty-cart') {
        apiFetch(API.CART_CLEAR, { method: 'POST', body: {} }).then(d => {
          if (d.success) {
            this.cartItems = [];
            this.cartTotal = 0;
            this.cartCount = 0;
            a11yNotify('warning', 'Carrito vaciado');
          }
        });
      } else if (action === 'cancel-order') {
        const orderId = data;
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = API.ORDER_CANCEL(orderId);
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCsrf();
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        this.orders = this.orders.map(o => o.id === orderId ? { ...o, status: 'cancelled', status_display: statusDisplay('cancelled') } : o);
        if (this.orderDetail && this.orderDetail.id === orderId) {
          this.orderDetail.status = 'cancelled';
          this.orderDetail.status_display = statusDisplay('cancelled');
        }
        form.submit();
      } else if (action === 'my-orders-cancel') {
        const orderId = data;
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = API.ORDER_CANCEL(orderId);
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCsrf();
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
      }
    },

    goToPayment() {
      const isLoggedIn = document.querySelector('meta[name="user-is-authenticated"]');
      if (!isLoggedIn || isLoggedIn.content !== 'true') {
        a11yNotify('warning', 'Inicia sesión', 'Debes iniciar sesión para continuar con el pago');
        this.showAuthModal = true;
        return;
      }
      window.location.href = API.PAGO + '?toast_type=info&toast_title=Redirigiendo%20al%20pago';
    },

    openPaymentModal() {
      this.goToPayment();
    },

    processPayment() {
      if (!this.paymentMethod) { if (!a11yNotify('warning', 'Selecciona un método de pago')) SwalWarning('Selecciona un método de pago'); return; }
      if (this.paymentMethod === 'cash' && this.montoRecibido < this.cartTotal) { if (!a11yNotify('warning', 'Monto insuficiente')) SwalWarning('Monto insuficiente'); return; }

      apiFetch(API.CHECKOUT, {
        method: 'POST',
        body: { payment_method: this.paymentMethod }
      }).then(d => {
        if (d.success) {
          this.openPayment = false;
          this.openCart = false;
          this.boletaData = d.order;
          this.showBoleta = true;
          this.cartItems = [];
          this.cartTotal = 0;
          this.cartCount = 0;
          a11yNotify('success', 'Pedido creado exitosamente');
        } else {
          if (!a11yNotify('error', 'Error', d.error || 'No se pudo procesar el pago.')) SwalError('Error', d.error || 'No se pudo procesar el pago.');
        }
      }).catch(() => { if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.'); });
    },

    loadOrders() {
      apiFetch(API.ORDER_DATA).then(d => {
        if (d.success) { this.orders = d.orders; }
      }).catch(() => { this.orders = []; });
    },

    viewOrderDetail(orderId) {
      apiFetch(API.ORDER_DETAIL(orderId)).then(d => {
        if (d.success) { this.orderDetail = d.order; this.openOrderDetail = true; }
      });
    },

    cancelOrder(orderId) {
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
  };
}
