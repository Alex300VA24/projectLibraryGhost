const ORDER_STATUS_MAP = {
  pending: 'bg-yellow-100 text-yellow-700',
  ready: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-red-100 text-red-600',
};

const ADMIN_ORDER_STATUS_MAP = {
  'Pendiente': 'bg-yellow-100 text-yellow-700',
  'Listo para entrega': 'bg-green-100 text-green-700',
  'Completado': 'bg-blue-100 text-blue-700',
  'Cancelado': 'bg-red-100 text-red-600',
};

const ADMIN_VENTA_STATUS_MAP = {
  'Completada': 'bg-green-100 text-green-700',
  'Pendiente': 'bg-yellow-100 text-yellow-700',
  'Cancelada': 'bg-red-100 text-red-600',
};

const STATUS_DISPLAY = {
  pending: 'Pendiente',
  ready: 'Listo para entrega',
  completed: 'Completado',
  cancelled: 'Cancelado',
};

const STATUS_ICONS = {
  pending: 'fa-regular fa-clock',
  ready: 'fa-solid fa-box',
  completed: 'fa-solid fa-check',
  cancelled: 'fa-solid fa-xmark',
  'Pendiente': 'fa-regular fa-clock',
  'Listo para entrega': 'fa-solid fa-box',
  'Completado': 'fa-solid fa-check',
  'Cancelado': 'fa-solid fa-xmark',
  'Completada': 'fa-solid fa-check',
  'Cancelada': 'fa-solid fa-xmark',
};

// Etiquetas legibles de método de pago
const PAYMENT_LABEL_MAP = {
  'yape':      'Yape',
  'plin':      'Plin',
  'cash':      'Efectivo',
  'transfer':  'Transferencia',
  'transferencia_bcp': 'Transferencia BCP',
  'transferencia_interbank': 'Transferencia Interbank',
  // display strings fallback
  'Yape':      'Yape',
  'Plin':      'Plin',
  'Efectivo':  'Efectivo',
  'Transferencia': 'Transferencia',
};

const BANK_LABEL_MAP = {
  'bcp':       'BCP',
  'interbank': 'Interbank',
};

// Clases CSS para badge de método de pago
const PAYMENT_BADGE_MAP = {
  'yape':      'badge-yape',
  'plin':      'badge-plin',
  'cash':      'badge-cash',
  'transfer':  'badge-bcp',  // default, override with bank
  'transferencia_bcp': 'badge-bcp',
  'transferencia_interbank': 'badge-interbank',
  'Yape':      'badge-yape',
  'Plin':      'badge-plin',
  'Efectivo':  'badge-cash',
  'Transferencia': 'badge-bcp',
};

export function orderBadgeClass(status) {
  return ORDER_STATUS_MAP[status] || 'bg-red-100 text-red-600';
}

export function adminOrderBadgeClass(status) {
  return ADMIN_ORDER_STATUS_MAP[status] || 'bg-purple-100 text-purple-700';
}

export function adminVentaBadgeClass(status) {
  return ADMIN_VENTA_STATUS_MAP[status] || 'bg-red-100 text-red-600';
}

export function statusIcon(status) {
  return STATUS_ICONS[status] || 'fa-solid fa-circle';
}

export function isOrderCancellable(status) {
  return status === 'pending';
}

export function statusDisplay(status) {
  return STATUS_DISPLAY[status] || status;
}

export function statusBadgeHTML(status, map_type = 'order') {
  const cls = map_type === 'admin_order' ? adminOrderBadgeClass(status)
    : map_type === 'admin_venta' ? adminVentaBadgeClass(status)
    : orderBadgeClass(status);
  const icon = statusIcon(status);
  const label = statusDisplay(status);
  return `<span class="badge ${cls}" data-status="${status}"><i class="${icon}"></i> ${label}</span>`;
}

/**
 * Returns the human-readable payment label including bank name for transfers.
 * @param {string} metodoKey - e.g. 'yape', 'plin', 'cash', 'transfer'
 * @param {string} transferBank - e.g. 'bcp', 'interbank' (only used when metodoKey==='transfer')
 */
export function paymentLabel(metodoKey, transferBank) {
  if (metodoKey === 'transferencia_interbank') return 'Transferencia Interbank';
  if (metodoKey === 'transferencia_bcp') return 'Transferencia BCP';
  const base = PAYMENT_LABEL_MAP[metodoKey] || metodoKey || '—';
  if ((metodoKey === 'transfer' || metodoKey === 'Transferencia') && transferBank) {
    const bank = BANK_LABEL_MAP[transferBank] || transferBank.toUpperCase();
    return `Transferencia ${bank}`;
  }
  return base;
}

/**
 * Returns the CSS badge class for a payment method.
 * @param {string} metodoKey
 * @param {string} transferBank
 */
export function paymentBadgeClass(metodoKey, transferBank) {
  if (metodoKey === 'transferencia_interbank') return 'badge-interbank';
  if (metodoKey === 'transferencia_bcp') return 'badge-bcp';
  if ((metodoKey === 'transfer' || metodoKey === 'Transferencia') && transferBank) {
    return transferBank === 'interbank' ? 'badge-interbank' : 'badge-bcp';
  }
  return PAYMENT_BADGE_MAP[metodoKey] || 'bg-ink-100 text-ink-600';
}
