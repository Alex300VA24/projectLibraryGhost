import { apiFetch } from '../services/api.js';
import { SwalToast } from '../utils/swal.js';
import { a11yNotify } from '../utils/notify.js';

export function productDetailApp(config = {}) {
  return {
    qty: 1,
    addToCart(productId) {
      apiFetch(config.addToCartUrl || '/carrito/agregar/', {
        method: 'POST',
        body: { product_id: productId, quantity: this.qty }
      }).then(d => {
        if (d.success) {
          if (!a11yNotify('success', 'Producto agregado al carrito')) SwalToast('success', '¡Producto agregado al carrito!');
          window.dispatchEvent(new CustomEvent('ym:cartUpdated', { detail: { count: d.cart_count, showCart: true } }));
        }
      });
    },
  };
}
