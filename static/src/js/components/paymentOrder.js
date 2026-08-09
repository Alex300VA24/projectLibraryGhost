import { apiFetch } from '../services/api.js';
import { usePolling } from '../composables/usePolling.js';
import { API } from '../services/urls.js';
import { a11yNotify } from '../utils/notify.js';

export function paymentOrderApp() {
  return {
    loading: true,
    orderId: null,
    orderNumber: '',
    boletaCode: '',
    paymentMethod: '',
    paymentMethodDisplay: '',
    transferBank: '',
    yapeType: '',
    generatedYapeCode: '',
    total: 0,
    items: [],
    isPaid: false,
    simulationUrl: '',
    simulationQrB64: '',
    yapeChoice: '',
    yapeCodeInput: '',
    codeError: false,
    polling: null,

    init() {
      const pathParts = window.location.pathname.split('/');
      const orderId = pathParts[pathParts.length - 2];
      this.orderId = orderId;

      apiFetch(API.PAYMENT_DATA(orderId)).then(data => {
        if (data.success) {
          const o = data.order;
          this.paymentMethod = o.payment_method;
          this.paymentMethodDisplay = o.payment_method_display;
          this.transferBank = o.transfer_bank;
          this.yapeType = o.yape_type;
          this.generatedYapeCode = o.generated_yape_code || '';
          this.total = o.total;
          this.items = o.items;
          this.isPaid = o.is_paid;
          this.boletaCode = o.boleta_code;
          this.orderNumber = o.order_number || String(orderId).padStart(6, '0');
          this.simulationUrl = this.buildSimulationUrl(o);
          this.simulationQrB64 = o.simulation_qr_b64 || '';
          this.loading = false;

          if (!o.is_paid && !(o.payment_method === 'yape' && o.yape_type === 'code')) {
            this.startPolling();
          }
        }
      }).catch(() => { this.loading = false; });
    },

    buildSimulationUrl(order) {
      const urls = {
        yape: API.PAYMENT_SIM_YAPE(order.id),
        plin: API.PAYMENT_SIM_PLIN(order.id),
        transferencia_bcp: API.PAYMENT_SIM_BCP(order.id),
        transferencia_interbank: API.PAYMENT_SIM_INTERBANK(order.id),
      };
      return urls[order.payment_method] || API.PAYMENT_SIM_YAPE(order.id);
    },

    startPolling() {
      this.polling = usePolling(() => {
        apiFetch(API.PAYMENT_CHECK(this.orderId)).then(data => {
          if (data.is_paid) {
            this.polling.stop();
            this.isPaid = true;
            this.boletaCode = data.boleta_code;
            a11yNotify('success', 'Pago confirmado', 'Pedido pagado correctamente');
          }
        });
      });
      this.polling.start();
    },

    validateYapeCode() {
      this.codeError = false;
      apiFetch(API.PAYMENT_YAPE_CODE(this.orderId, this.yapeCodeInput)).then(data => {
        if (data.success) {
          if (this.polling) this.polling.stop();
          this.isPaid = true;
          this.boletaCode = data.boleta_code;
          a11yNotify('success', 'Pago confirmado', 'Código Yape validado correctamente');
        } else {
          this.codeError = true;
          a11yNotify('error', 'Código incorrecto', 'El código Yape ingresado no es válido');
        }
      });
    }
  };
}
