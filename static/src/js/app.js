import Alpine from 'alpinejs';
import collapse from '@alpinejs/collapse';
import Swal from 'sweetalert2';
import { initCsrf } from './services/api.js';
import { orderBadgeClass, adminOrderBadgeClass, adminVentaBadgeClass, isOrderCancellable, statusDisplay, statusIcon, paymentLabel, paymentBadgeClass } from './utils/status.js';
import { navbarApp } from './components/navbar.js';
import { catalogApp } from './components/catalog.js';
import { contactApp } from './components/contact.js';
import { productDetailApp } from './components/productDetail.js';
import { pagoApp } from './components/pago.js';
import { paymentOrderApp } from './components/paymentOrder.js';
import { adminApp } from './components/admin.js';
import { orderPage } from './components/myOrders.js';
import { saveProfile, changePassword } from './components/profile.js';
import { accessibilityApp } from './components/accessibility.js';

Alpine.plugin(collapse);

initCsrf();

window.Alpine = Alpine;
window.Swal = Swal;
window.navbarApp = navbarApp;
window.catalogApp = catalogApp;
window.contactApp = contactApp;
window.productDetailApp = productDetailApp;
window.pagoApp = pagoApp;
window.paymentOrderApp = paymentOrderApp;
window.adminApp = adminApp;
window.orderPage = orderPage;
window.saveProfile = saveProfile;
window.changePassword = changePassword;
window.accessibilityApp = accessibilityApp;
window.orderBadgeClass = orderBadgeClass;
window.adminOrderBadgeClass = adminOrderBadgeClass;
window.adminVentaBadgeClass = adminVentaBadgeClass;
window.isOrderCancellable = isOrderCancellable;
window.statusDisplay = statusDisplay;
window.statusIcon = statusIcon;
window.paymentLabel = paymentLabel;
window.paymentBadgeClass = paymentBadgeClass;

Alpine.start();
