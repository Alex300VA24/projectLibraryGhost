import { apiFetch } from '../services/api.js';
import { SwalError, SwalSuccess, SwalWarning } from '../utils/swal.js';
import { usePolling } from '../composables/usePolling.js';
import { API } from '../services/urls.js';
import { a11yNotify } from '../utils/notify.js';
import { adminOrderBadgeClass, adminVentaBadgeClass, statusIcon, paymentLabel, paymentBadgeClass } from '../utils/status.js';

export function adminApp(config = {}) {
  return {
    sidebarOpen: true,
    sidebarMobileOpen: false,
    adminSection: config.freshLogin ? config.defaultSection : (localStorage.getItem('ym_section') || config.defaultSection || 'dashboard'),
    openSubmenu: config.freshLogin ? config.defaultSubmenu : (localStorage.getItem('ym_submenu') || config.defaultSubmenu || null),
    ventaTab: localStorage.getItem('ym_ventaTab') || 'manual',
    usuarioTab: 'todos',
    ayudaTab: 'docs',
    loading: false,
    loadingAction: '',
    loadingCrearUsuario: false,
    cancelandoVenta: false,

    busquedaInventario: '',
    filtroCategoria: '',
    busquedaPedido: '',
    filtroEstadoPedido: '',
    busquedaVentaProducto: '',
    metodoPago: 'Efectivo',
    montoRecibido: 0,
    carrito: [],
    pagoStep: 1,
    pagoQRB64: '',
    pagoSimulationUrl: '',
    pagoOrderId: null,
    pagoBoletaCode: '',
    pagoPolling: null,
    scanQueuePolling: null,
    filtroFechaVenta: '',
    filtroCanalVenta: '',
    filtroTrabajadorVenta: '',
    busquedaVentaId: '',
    busquedaGasto: '',
    filtroFechaGasto: '',
    filtroTipoGasto: '',
    busquedaUsuario: '',
    filtroRolUsuario: '',
    PER_PAGE: 10,
    trabajadores: [],
    invPage: 1,
    ventasPage: 1,
    gastosPage: 1,
    usuariosPage: 1,

    showLoadingOverlay: false,
    showModalVerProducto: false,
    showModalRegistrarLote: false,
    showModalAgregarProducto: false,
    showModalConfirmarEliminarProducto: false,
    showModalVerPedido: false,
    showModalPrepararPedido: false,
    showModalQRScanner: false,
    pedidoPreparar: { id: null, cliente: '', fecha: '', metodo_pago: '', direccion: '', estado: '', items: [], total: 0, notes: '', estado_key: '' },
    pedidoQR: { id: null, estado_key: '', estado: '', cliente: '', items: [], total: 0 },
    loadingListo: false,
    loadingQR: false,
    qrCodigoManual: '',
    loadingQRManual: false,
    codigoManualUsado: false,
    showModalVerVenta: false,
    showModalVerBoleta: false,
    boletaData: null,
    showModalEditarVenta: false,
    showModalAgregarGasto: false,
    showModalVerGasto: false,
    showModalConfirmarEliminarGasto: false,
    showModalCrearTrabajador: false,
    showModalVerUsuario: false,
    showModalEditarUsuario: false,
    showModalConfirmarDesactivar: false,
    showModalGuia: false,
    showModalPago: false,
    showModalBoleta: false,
    showModalExportar: false,
    showModalNotificaciones: false,
    showModalCancelarPedido: false,
    showModalCancelarVenta: false,
    showModalResetPassword: false,
    exportarFormato: '',
    exportarTitulo: '',
    exportarRangoFecha: { inicio: '', fin: '' },
    reportesSubView: 'ventas',
    topProdPage: 1,
    stockPage: 1,
    stockBajoPage: 1,

    productoVer: null,
    productoEliminar: null,
    pedidoVer: null,
    ventaVer: null,
    ventaEditar: { id: null, cliente: '', total: 0, metodo: '', canal: '', estado: '', justificacion: '', fecha: '', items: [], boleta_code: '' },
    gastoVer: null,
    gastoEliminar: null,
    usuarioVer: null,
    usuarioEditar: { id: null, nombre: '', apellido: '', email: '', telefono: '', rol: 'employee', username: '' },
    usuarioDesactivar: null,
    boletaVenta: null,
    pedidoCancelar: null,
    ventaCancelar: null,
    justificacionCancelarPedido: '',
    justificacionCancelarVenta: '',

    formProducto: { id: null, nombre: '', codigo: '', categoria: '', precio: 0, umbral: 10, descripcion: '', color: '#d97706', icono: 'fa-solid fa-box', imagen: null, imagenFile: null, imagenPreview: null },
    formGasto: { id: null, concepto: '', tipo: 'Variable', monto: 0, fecha: '', descripcion: '', comprobanteFile: null, comprobantePreview: null },
    formLote: { modo: 'create', productoId: null, productoNombre: '', productoCodigo: '', productoColor: '', productoIcono: '', productoImagen: null, loteId: null, numeroLote: '', proveedor: '', precio: 0, cantidad: 0, fechaVencimiento: '' },
    formNuevoUsuario: { nombre: '', apellido: '', email: '', telefono: '', rol: 'employee', username: '' },
    guiaTitulo: '',
    guiaPasos: [],
    errorTelefonoCrear: '',
    errorTelefonoEditar: '',
    errorNombreCrear: '',
    errorApellidoCrear: '',
    errorUsernameCrear: '',
    errorEmailCrear: '',
    errorNombreEditar: '',
    errorApellidoEditar: '',
    errorUsernameEditar: '',
    errorEmailEditar: '',
    errorNombreProducto: '',
    errorCategoriaProducto: '',
    errorPrecioProducto: '',
    errorPrecioLote: '',
    errorCantidadLote: '',
    errorFechaLote: '',
    errorProveedorLote: '',

    errorConceptoGasto: '',
    errorTipoGasto: '',
    errorMontoGasto: '',
    errorFechaGasto: '',

    currentUser: {
      nombre: config.username || '',
      email: config.email || '',
      rol: config.role || ''
    },

    weekOffset: 0,
    dashboardData: { ventasHoy: 0, gastosHoy: 0, gananciaHoy: 0, ventasSemana: 0, gastosSemana: 0, gastosSemanaAnterior: 0, gananciaSemana: 0, ventasMes: 0, gastosMes: 0, gananciaMes: 0, gastosTotal: 0, stockBajo: 0, pedidosPendientes: 0, utilidadNeta: 0 },
    chartData: [],
    topProductos: [],
    productos: [],
    pedidos: [],
    ventas: [],
    gastos: [],
    usuarios: [],
    categorias: [],

    get initial() { return this.currentUser.nombre.charAt(0).toUpperCase(); },
    get isEmpleado() { return this.currentUser.rol === 'employee' || this.currentUser.rol === 'empleado'; },
    get isAdmin() { return this.currentUser.rol === 'admin'; },

    get filteredSidebarItems() {
      if (this.isAdmin) return this.sidebarItems;
      const allowed = ['inventario', 'ventas', 'ayuda'];
      return this.sidebarItems.filter(item => allowed.includes(item.id));
    },

    navigateTo(section) {
      if (this.isEmpleado) {
        const allowed = ['inventario', 'nueva-venta', 'lista-ventas', 'ayuda'];
        if (!allowed.includes(section)) return;
      }
      this.adminSection = section;
      localStorage.setItem('ym_section', section);
      if (section === 'nueva-venta' || section === 'lista-ventas') {
        this.openSubmenu = 'ventas';
        localStorage.setItem('ym_submenu', 'ventas');
      } else {
        this.openSubmenu = null;
        localStorage.removeItem('ym_submenu');
      }
    },

    sidebarItems: [
      { id: 'dashboard', label: 'Inicio', icon: 'fa-solid fa-school' },
      { id: 'inventario', label: 'Inventario', icon: 'fa-solid fa-book-open' },
      { id: 'ventas', label: 'Ventas', icon: 'fa-solid fa-cart-shopping', children: [
        { id: 'nueva-venta', label: 'Nueva Venta', icon: 'fa-solid fa-cash-register' },
        { id: 'lista-ventas', label: 'Lista de Ventas', icon: 'fa-solid fa-list-check' }
      ]},
      { id: 'gastos', label: 'Gastos', icon: 'fa-solid fa-coins' },
      { id: 'usuarios', label: 'Usuarios', icon: 'fa-solid fa-chalkboard-user' },
      { id: 'ayuda', label: 'Ayuda', icon: 'fa-solid fa-graduation-cap' }
    ],

    get maxChartVenta() { return Math.max(...this.chartData.map(d => d.ventas), 1); },

    get filteredInventario() {
      const result = this.productos.filter(p => {
        const matchSearch = !this.busquedaInventario || p.nombre.toLowerCase().includes(this.busquedaInventario.toLowerCase()) || p.codigo.toLowerCase().includes(this.busquedaInventario.toLowerCase());
        const matchCat = !this.filtroCategoria || p.categoria === this.filtroCategoria;
        return matchSearch && matchCat;
      });
      if (this.invPage > Math.ceil(result.length / this.PER_PAGE)) this.invPage = 1;
      return result;
    },

    get filteredPedidos() { return this.pedidos; },

    get filteredPedidosOnline() {
      let result = this.pedidos;
      if (this.busquedaPedido) {
        const q = this.busquedaPedido.toLowerCase();
        result = result.filter(p => p.cliente.toLowerCase().includes(q) || String(p.id).includes(q) || (p.boleta_code && p.boleta_code.toLowerCase().includes(q)));
      }
      if (this.filtroEstadoPedido) {
        result = result.filter(p => p.estado_key === this.filtroEstadoPedido);
      }
      return result;
    },

    get filteredVentaProductos() {
      if (!this.busquedaVentaProducto) return this.productos.filter(p => this.productoStock(p) > 0);
      return this.productos.filter(p => this.productoStock(p) > 0 && (p.nombre.toLowerCase().includes(this.busquedaVentaProducto.toLowerCase()) || p.codigo.toLowerCase().includes(this.busquedaVentaProducto.toLowerCase())));
    },

    get _ventaBruta() { return this.carrito.reduce((s, item) => s + item.precio * item.cantidad, 0); },
    get ventaSubtotal() { return this._ventaBruta / 1.18; },
    get ventaIGV() { return this._ventaBruta * 0.18 / 1.18; },
    get ventaTotal() { return this._ventaBruta; },

    get filteredUsuarios() {
      const result = this.usuarios.filter(u => {
        const matchSearch = !this.busquedaUsuario || u.nombre.toLowerCase().includes(this.busquedaUsuario.toLowerCase()) || u.email.toLowerCase().includes(this.busquedaUsuario.toLowerCase());
        const matchRol = !this.filtroRolUsuario || u.rol === this.filtroRolUsuario;
        return matchSearch && matchRol;
      });
      if (this.usuariosPage > Math.ceil(result.length / this.PER_PAGE)) this.usuariosPage = 1;
      return result;
    },

    faqs: [
      { pregunta: 'Como agrego un producto al inventario?', respuesta: 'Ve a Inventario y haz clic en "Agregar Producto". Completa nombre, categoria, precio y umbral de stock. El codigo se genera automaticamente. Luego registra lotes con el boton (+) del producto.', abierto: false },
      { pregunta: 'Como gestiono los pedidos online?', respuesta: 'En Pedidos Online veras los pedidos pendientes. Prepara el pedido, marcalo como "Listo para entrega" y usa el escaner QR o codigo de boleta para confirmar la entrega.', abierto: false },
      { pregunta: 'Que hago cuando un producto tiene stock bajo?', respuesta: 'El sistema marca en rojo los productos por debajo del umbral. Registra un lote nuevo desde el boton (+) del producto en Inventario para reponer stock.', abierto: false },
      { pregunta: 'Como registro un gasto?', respuesta: 'Ve a Gastos y haz clic en "Registrar Gasto". Selecciona el tipo (Fijo, Variable, Operativo, Mantenimiento), ingresa monto, fecha y descripcion. Puedes adjuntar comprobante (imagen o PDF).', abierto: false },
      { pregunta: 'Como creo un usuario empleado?', respuesta: 'En Usuarios, haz clic en "Registrar Usuario". Completa nombre, email y rol. La contrasena inicial es "Cambiar123++" y el usuario debera cambiarla en su primer ingreso.', abierto: false }
    ],

    paginatedItems(items, page) {
      const total = items.length;
      const totalPages = Math.max(1, Math.ceil(total / this.PER_PAGE));
      const currentPage = Math.min(page, totalPages);
      const start = (currentPage - 1) * this.PER_PAGE;
      return { items: items.slice(start, start + this.PER_PAGE), totalPages, currentPage, total };
    },

    getPageRange(currentPage, totalPages) {
      const pages = [];
      if (totalPages <= 7) {
        for (let i = 1; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        if (currentPage > 3) pages.push('...');
        for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
          pages.push(i);
        }
        if (currentPage < totalPages - 2) pages.push('...');
        pages.push(totalPages);
      }
      return pages;
    },

    _notify(title, icon) {
      if (a11yNotify(icon || 'success', title)) return;
      return SwalSuccess(title);
    },
    beginAction(action) {
      if (this.loadingAction) return false;
      this.loadingAction = action;
      return true;
    },
    endAction(action) {
      if (this.loadingAction === action) this.loadingAction = '';
    },
    isActionLoading(action) { return this.loadingAction === action; },

    loadDashboard(offset) { if (offset !== undefined) this.weekOffset = offset; return apiFetch(API.DASHBOARD_STATS + '?offset=' + this.weekOffset).then(d => { if (d.ventasSemana !== undefined) { this.dashboardData = d; this.chartData = d.chartData || []; this.topProductos = d.topProductos || []; } }); },
    navegarSemana(dir) { this.loadDashboard(this.weekOffset + dir); },
    loadProductos() {
      return apiFetch(API.DASHBOARD_PRODUCTOS + '?_=' + Date.now()).then(d => { if (d.productos) this.productos = d.productos; });
    },
    loadPedidos() { apiFetch(API.DASHBOARD_PEDIDOS).then(d => { if (d.pedidos) this.pedidos = d.pedidos; }); },
    loadVentas() { return apiFetch(API.DASHBOARD_VENTAS + '?_=' + Date.now()).then(d => { if (d.ventas) this.ventas = d.ventas; if (d.trabajadores) this.trabajadores = d.trabajadores; }); },
    refreshVentas() { return Promise.all([this.loadVentas(), this.loadProductos(), this.loadDashboard()]); },
    loadGastos() { apiFetch(API.DASHBOARD_GASTOS).then(d => { if (d.gastos) this.gastos = d.gastos; }); },
    loadUsuarios() { apiFetch(API.DASHBOARD_USUARIOS).then(d => { if (d.usuarios) this.usuarios = d.usuarios; }); },
    loadCategorias() { apiFetch(API.DASHBOARD_CATEGORIAS).then(d => { if (d.categorias) this.categorias = d.categorias; }); },

    init() {
      this.loadDashboard();
      this.loadProductos();
      this.loadPedidos();
      this.loadVentas();
      this.loadGastos();
      this.loadUsuarios();
      this.loadCategorias();
      // this.startScanQueuePolling();
      // this.$watch('ventaTab', val => {
      //   localStorage.setItem('ym_ventaTab', val);
      //   if (val === 'manual') {
      //     this.startScanQueuePolling();
      //   } else {
      //     this.stopScanQueuePolling();
      //   }
      // });
      this.$watch('busquedaVentaId', () => { this.ventasPage = 1; });
      this.$watch('filtroFechaVenta', () => { this.ventasPage = 1; });
      this.$watch('filtroCanalVenta', () => { this.ventasPage = 1; });
      this.$watch('filtroTrabajadorVenta', () => { this.ventasPage = 1; });
      this.$watch('busquedaGasto', () => { this.gastosPage = 1; });
      this.$watch('filtroFechaGasto', () => { this.gastosPage = 1; });
      this.$watch('filtroTipoGasto', () => { this.gastosPage = 1; });
      this.$watch('busquedaInventario', () => { this.invPage = 1; });
      this.$watch('filtroCategoria', () => { this.invPage = 1; });
      document.addEventListener('keydown', e => {
        if (e.ctrlKey && e.key === 'k') {
          e.preventDefault();
          const searchInput = document.querySelector('[x-model="busquedaInventario"]');
          if (searchInput) {
            this.adminSection = 'inventario';
            this.$nextTick(() => searchInput.focus());
          }
        }
        if (e.altKey) {
          const navMap = { '1': 'dashboard', '2': 'inventario', '3': 'nueva-venta', '4': 'lista-ventas', '5': 'gastos', '6': 'usuarios', '7': 'ayuda' };
          if (navMap[e.key]) {
            e.preventDefault();
            this.navigateTo(navMap[e.key]);
          }
        }
      });
    },

    getPageTitle() {
      const titles = { 'dashboard': 'Inicio', 'inventario': 'Inventario', 'nueva-venta': 'Nueva Venta', 'lista-ventas': 'Lista de Ventas', 'gastos': 'Gastos', 'usuarios': 'Usuarios', 'ayuda': 'Centro de Ayuda' };
      return titles[this.adminSection] || 'Inicio';
    },

    getPageIcon() {
      const icons = { 'dashboard': 'fa-solid fa-store', 'inventario': 'fa-solid fa-boxes-stacked', 'nueva-venta': 'fa-solid fa-truck-fast', 'lista-ventas': 'fa-solid fa-list', 'gastos': 'fa-solid fa-receipt', 'usuarios': 'fa-solid fa-users-gear', 'ayuda': 'fa-solid fa-circle-question' };
      return icons[this.adminSection] || 'fa-solid fa-store';
    },

    isActive(id) { return this.adminSection === id; },

    toggleSubmenu(id) {
      this.openSubmenu = this.openSubmenu === id ? null : id;
      if (this.openSubmenu) localStorage.setItem('ym_submenu', this.openSubmenu);
      else localStorage.removeItem('ym_submenu');
    },

    productoPrecio(prod) { return prod?.precio || 0; },
    productoCosto(prod) { return prod?.lotes && prod.lotes.length > 0 ? prod.lotes[prod.lotes.length - 1].precio : 0; },
    productoStock(prod) { return prod?.lotes ? prod.lotes.reduce((s, l) => s + l.cantidad, 0) : 0; },

    verProducto(prod) { this.productoVer = prod; this.showModalVerProducto = true; },
    editarProducto(prod) { this.formProducto = { ...prod, imagenFile: null, imagenPreview: null }; this.errorNombreProducto = ''; this.errorCategoriaProducto = ''; this.errorPrecioProducto = ''; this.showModalAgregarProducto = true; },
    confirmarEliminarProducto(prod) { this.productoEliminar = prod; this.showModalConfirmarEliminarProducto = true; },
    eliminarProducto() {
      if (!this.productoEliminar || !this.beginAction('eliminarProducto')) return;
      apiFetch(API.DASHBOARD_PRODUCTO(this.productoEliminar.id), { method: 'DELETE' }).then(() => {
        this.productos = this.productos.filter(p => p.id !== this.productoEliminar.id);
        this.showModalConfirmarEliminarProducto = false;
        this._notify('Producto eliminado');
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => this.endAction('eliminarProducto'));
    },

    validarProducto() {
      var ok = true;
      if (!this.formProducto.nombre || this.formProducto.nombre.trim() === '') {
        this.errorNombreProducto = 'El nombre es obligatorio.'; ok = false;
      } else if (this.formProducto.nombre.trim().length < 2) {
        this.errorNombreProducto = 'Minimo 2 caracteres.'; ok = false;
      } else { this.errorNombreProducto = ''; }

      if (!this.formProducto.categoria || this.formProducto.categoria.trim() === '') {
        this.errorCategoriaProducto = 'Selecciona una categoria.'; ok = false;
      } else { this.errorCategoriaProducto = ''; }

      var precio = Number(this.formProducto.precio);
      if (!this.formProducto.precio || isNaN(precio) || precio <= 0) {
        this.errorPrecioProducto = 'Ingresa un precio valido mayor a 0.'; ok = false;
      } else { this.errorPrecioProducto = ''; }

      return ok;
    },

    guardarProducto() {
      if (!this.validarProducto() || !this.beginAction('guardarProducto')) return;
      const formData = new FormData();
      formData.append('nombre', this.formProducto.nombre || '');
      formData.append('codigo', this.formProducto.codigo || '');
      formData.append('categoria', this.formProducto.categoria || 'Alimentos');
      formData.append('precio', this.formProducto.precio || 0);
      formData.append('umbral', this.formProducto.umbral || 10);
      formData.append('descripcion', this.formProducto.descripcion || '');
      formData.append('color', this.formProducto.color || '#d97706');
      if (this.formProducto.imagenFile) formData.append('imagen', this.formProducto.imagenFile);
      const url = this.formProducto.id ? API.DASHBOARD_PRODUCTO(this.formProducto.id) : API.DASHBOARD_PRODUCTOS;
      fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || '' },
        body: formData
      }).then(r => r.json()).then(d => {
        if (d && d.success === false) throw new Error(d.error || 'No se pudo guardar el producto');
        this.loadProductos();
        this.showModalAgregarProducto = false;
        if (!a11yNotify('success', this.formProducto.id ? 'Producto actualizado' : 'Producto registrado')) SwalSuccess(this.formProducto.id ? 'Producto actualizado' : 'Producto registrado');
      }).catch(error => { if (!a11yNotify('error', 'Error', error.message || 'No se pudo guardar el producto')) SwalError('Error', error.message || 'No se pudo guardar el producto'); })
        .finally(() => this.endAction('guardarProducto'));
    },
    resetFormProducto() { this.formProducto = { id: null, nombre: '', codigo: '', categoria: 'Alimentos', precio: 0, umbral: 10, descripcion: '', color: '#d97706', icono: 'fa-solid fa-box', imagen: null, imagenFile: null, imagenPreview: null }; },
    handleProductoImagen(event) {
      const file = event.target.files[0];
      if (file) {
        this.formProducto.imagenFile = file;
        const reader = new FileReader();
        reader.onload = e => { this.formProducto.imagenPreview = e.target.result; };
        reader.readAsDataURL(file);
      }
    },

    verPedido(pedido) { this.pedidoVer = pedido; this.showModalVerPedido = true; },

    verPedidoOnline(pedido) {
      this.loadingListo = false;
      this.loadingQR = false;
      apiFetch(API.DASHBOARD_PEDIDO_DETALLE(pedido.id)).then(d => {
        if (d.success && d.order) {
          this.pedidoPreparar = d.order;
          this.showModalPrepararPedido = true;
        }
      });
    },

    marcarListoEntrega(pedido) {
      if (this.showLoadingOverlay) return;
      this.showLoadingOverlay = true;
      apiFetch(API.DASHBOARD_PEDIDO_LISTO(pedido.id), { method: 'POST' }).then(d => {
        this.showLoadingOverlay = false;
        if (d.success) {
          this.showModalPrepararPedido = false;
          this.loadPedidos();
          if (!a11yNotify('success', 'Pedido listo', 'Se ha notificado al cliente por correo.')) SwalSuccess('Pedido listo', 'Se ha notificado al cliente por correo.');
        } else {
          if (!a11yNotify('error', 'Error', d.error || 'No se pudo actualizar el pedido')) SwalError('Error', d.error || 'No se pudo actualizar el pedido');
        }
      }).catch(() => {
        this.showLoadingOverlay = false;
        if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.');
      });
    },

    marcarListoDirecto(pedido) {
      if (this.showLoadingOverlay) return;
      this.showLoadingOverlay = true;
      apiFetch(API.DASHBOARD_PEDIDO_LISTO(pedido.id), { method: 'POST' }).then(d => {
        this.showLoadingOverlay = false;
        if (d.success) {
          this.loadPedidos();
          if (!a11yNotify('success', 'Pedido listo', 'El pedido está listo para entrega.')) SwalSuccess('Pedido listo', 'El pedido está listo para entrega.');
        } else {
          if (!a11yNotify('error', 'Error', d.error || 'No se pudo actualizar el pedido')) SwalError('Error', d.error || 'No se pudo actualizar el pedido');
        }
      }).catch(() => {
        this.showLoadingOverlay = false;
        if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.');
      });
    },

    abrirQRScanner(pedido) {
      this.pedidoQR = null;
      this.qrCodigoManual = '';
      this.loadingQRManual = false;
      this.codigoManualUsado = false;
      apiFetch(API.DASHBOARD_PEDIDO_DETALLE(pedido.id)).then(d => {
        if (d.success && d.order) {
          this.pedidoQR = d.order;
          this.showModalQRScanner = true;
          if (d.order.estado_key === 'ready') {
            this.startQRPolling(pedido.id);
          }
        }
      });
    },

    completarPedidoQR(pedido) {
      if (this.showLoadingOverlay) return;
      this.showModalQRScanner = false;
      this.showLoadingOverlay = true;
      apiFetch(API.DASHBOARD_PEDIDO_COMPLETAR_QR(pedido.id), { method: 'POST' }).then(d => {
        this.showLoadingOverlay = false;
        this.loadingQR = false;
        if (d.success) {
          this.stopQRPolling();
          this.loadPedidos();
          this.loadVentas();
          this.loadDashboard();
          if (!a11yNotify('success', 'Código escaneado correctamente', 'El código QR fue escaneado con éxito y el pedido ha sido completado.')) SwalSuccess('Código escaneado correctamente', 'El código QR fue escaneado con éxito y el pedido ha sido completado.');
        } else {
          if (!a11yNotify('error', 'Error', d.error || 'No se pudo completar el pedido')) SwalError('Error', d.error || 'No se pudo completar el pedido');
        }
      }).catch(() => {
        this.showLoadingOverlay = false;
        this.loadingQR = false;
        if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.');
      });
    },

    validarCodigoManual() {
      if (this.loadingQRManual) return;
      if (!this.qrCodigoManual || !this.qrCodigoManual.trim()) {
        if (!a11yNotify('warning', 'Código requerido', 'Ingresa el código de boleta del cliente.')) SwalError('Código requerido', 'Ingresa el código de boleta del cliente.');
        return;
      }
      this.loadingQRManual = true;
      this.showModalQRScanner = false;
      this.showLoadingOverlay = true;
      this.codigoManualUsado = true;
      apiFetch(API.DASHBOARD_QR_SCAN, {
        method: 'POST',
        body: { boleta_code: this.qrCodigoManual.trim() }
      }).then(d => {
        this.showLoadingOverlay = false;
        this.loadingQRManual = false;
        if (d.success) {
          this.stopQRPolling();
          this.loadPedidos();
          this.loadVentas();
          this.loadDashboard();
          if (!a11yNotify('success', 'Código validado correctamente', 'El código de boleta fue validado con éxito y el pedido ha sido completado.')) SwalSuccess('Código validado correctamente', 'El código de boleta fue validado con éxito y el pedido ha sido completado.');
        } else {
          this.codigoManualUsado = false;
          if (!a11yNotify('error', 'Error', d.error || 'No se pudo validar el código')) SwalError('Error', d.error || 'No se pudo validar el código');
        }
      }).catch(() => {
        this.showLoadingOverlay = false;
        this.loadingQRManual = false;
        this.codigoManualUsado = false;
        if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.');
      });
    },

    qrPollingInstance: null,

    startQRPolling(orderId) {
      this.stopQRPolling();
      this.qrPollingInstance = usePolling(() => {
        apiFetch(API.DASHBOARD_PEDIDO_DETALLE(orderId)).then(d => {
          if (d.success && d.order) {
            if (d.order.estado_key === 'completed' && this.showModalQRScanner && !this.codigoManualUsado) {
              this.stopQRPolling();
              this.showModalQRScanner = false;
              this.loadPedidos();
              if (!a11yNotify('success', 'Código escaneado correctamente', 'El código QR fue escaneado con éxito y el pedido ha sido completado.')) SwalSuccess('Código escaneado correctamente', 'El código QR fue escaneado con éxito y el pedido ha sido completado.');
            } else if (this.showModalQRScanner && this.pedidoQR) {
              this.pedidoQR = d.order;
            }
          }
        });
      });
      this.qrPollingInstance.start();
    },

    stopQRPolling() {
      if (this.qrPollingInstance) {
        this.qrPollingInstance.stop();
        this.qrPollingInstance = null;
      }
    },

    startScanQueuePolling() {
      this.stopScanQueuePolling();
      this.scanQueuePolling = usePolling(() => {
        apiFetch(API.SCAN_QUEUE_PENDING).then(data => {
          if (!data.items || data.items.length === 0) return;
          let consumedIds = [];
          data.items.forEach(item => {
            if (!item.product) return;
            let prod = this.productos.find(p => p.id === item.product.id);
            if (prod && this.productoStock(prod) > 0) {
              this.agregarAlCarrito(prod);
              consumedIds.push(item.id);
            }
          });
          if (consumedIds.length > 0) {
            apiFetch(API.SCAN_QUEUE_CONSUME, { method: 'POST', body: { ids: consumedIds } }).catch(() => {});
          }
        }).catch(() => {});
      });
      this.scanQueuePolling.start();
    },

    stopScanQueuePolling() {
      if (this.scanQueuePolling) {
        this.scanQueuePolling.stop();
        this.scanQueuePolling = null;
      }
    },


    cambiarEstadoPedido(pedido, nuevoEstado) {
      if (!pedido || !this.beginAction('cambiarEstadoPedido')) return Promise.resolve(false);
      return apiFetch(API.DASHBOARD_PEDIDO_ESTADO(pedido.id), {
        method: 'PUT', body: { estado: nuevoEstado }
      }).then(d => {
        if (d.success) {
          pedido.estado = nuevoEstado;
          this._notify('Pedido actualizado a: ' + nuevoEstado);
          this.loadDashboard();
          return true;
        }
        throw new Error(d.error || 'No se pudo actualizar el pedido.');
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
        return false;
      }).finally(() => this.endAction('cambiarEstadoPedido'));
    },

    cancelarPedidoAdmin(pedido) {
      this.pedidoCancelar = pedido;
      this.justificacionCancelarPedido = '';
      this.showModalCancelarPedido = true;
    },
    confirmarCancelarPedido() {
      if (!this.pedidoCancelar) return;
      this.cambiarEstadoPedido(this.pedidoCancelar, 'Cancelado').then(success => {
        if (success) this.showModalCancelarPedido = false;
      });
    },

    verVenta(venta) { this.ventaVer = venta; this.showModalVerVenta = true; },
    verBoleta(venta, autoPrint) {
      if (!venta.boleta_code) return;
      this.boletaData = { ...venta, items: [] };
      this.showModalVerBoleta = true;
      apiFetch(API.DASHBOARD_PEDIDO_DETALLE(venta.id)).then(d => {
        if (d.success && d.order) {
          this.boletaData = { ...this.boletaData, items: d.order.items || [], fecha: d.order.fecha || venta.fecha };
        }
        if (autoPrint) setTimeout(() => this.imprimirBoleta(this.boletaData), 300);
      });
    },
    imprimirBoleta(data) {
      if (!data) return;
      document.body.classList.add('printing-boleta');
      setTimeout(() => { window.print(); }, 100);
      window.addEventListener('afterprint', () => {
        document.body.classList.remove('printing-boleta');
      }, { once: true });
    },
    editarVenta(venta) { this.ventaEditar = { ...venta, justificacion: '' }; this.showModalEditarVenta = true; },
    cancelarVenta(venta) {
      this.ventaCancelar = venta;
      this.justificacionCancelarVenta = '';
      this.showModalCancelarVenta = true;
    },
    confirmarCancelarVenta() {
      const venta = this.ventaCancelar;
      if (!venta || this.cancelandoVenta) return;
      this.cancelandoVenta = true;

      apiFetch(API.DASHBOARD_VENTA_CANCELAR(venta.id), {
        method: 'POST',
        body: { justificacion: this.justificacionCancelarVenta || '' }
      }).then(d => {
        if (!d.success) throw new Error(d.error || 'No se pudo cancelar la venta.');
        this.showModalCancelarVenta = false;
        this.justificacionCancelarVenta = '';
        this.ventaCancelar = null;
        return this.refreshVentas();
      }).then(() => {
        if (!a11yNotify('success', 'Venta cancelada correctamente')) SwalSuccess('Venta cancelada correctamente');
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => { this.cancelandoVenta = false; });
    },
    guardarVenta() {
      const idx = this.ventas.findIndex(v => v.id === this.ventaEditar.id);
      if (idx >= 0) this.ventas[idx] = { ...this.ventaEditar };
      this.showModalEditarVenta = false;
    },

    abrirRegistrarLote(prod) {
      this.formLote = {
        modo: 'create', productoId: prod.id, productoNombre: prod.nombre, productoCodigo: prod.codigo,
        productoColor: prod.color, productoIcono: prod.icono, productoImagen: prod.imagen,
        loteId: null, numeroLote: '', proveedor: '', precio: 0, cantidad: 0, fechaVencimiento: ''
      };
      this.errorPrecioLote = ''; this.errorCantidadLote = ''; this.errorFechaLote = ''; this.errorProveedorLote = '';
      this.showModalRegistrarLote = true;
    },

    abrirEditarLote(prod) {
      const lotes = prod.lotes || [];
      const lote = lotes[0] || null;
      this.formLote = {
        modo: 'edit', productoId: prod.id, productoNombre: prod.nombre, productoCodigo: prod.codigo,
        productoColor: prod.color, productoIcono: prod.icono, productoImagen: prod.imagen,
        loteId: lote ? Number(lote.id) : null, numeroLote: lote ? lote.numeroLote : '', proveedor: lote ? lote.proveedor : '',
        precio: lote ? Number(lote.precio) : 0, cantidad: lote ? Number(lote.cantidad) : 0,
        fechaVencimiento: lote ? this.normalizeDateForInput(lote.fechaVencimiento) : ''
      };
      this.errorPrecioLote = ''; this.errorCantidadLote = ''; this.errorFechaLote = ''; this.errorProveedorLote = '';
      this.showModalRegistrarLote = true;
    },

    normalizeDateForInput(value) {
      if (!value) return '';
      if (/^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
        const [dia, mes, anio] = value.split('/');
        return `${anio}-${mes}-${dia}`;
      }
      return value;
    },

    currentLote() {
      try {
        const product = this.productos.find(p => p.id === this.formLote.productoId);
        if (!product) return null;
        const lotes = product.lotes || [];
        return lotes.find(l => Number(l.id) === Number(this.formLote.loteId)) || null;
      } catch(e) {
        return null;
      }
    },

    currentLoteIsLocked() {
      try {
        const lote = this.currentLote();
        return lote ? lote.isLocked : false;
      } catch(e) {
        return false;
      }
    },

    selectedProductoLotes() {
      try {
        const product = this.productos.find(p => p.id === this.formLote.productoId);
        return product ? (product.lotes || []) : [];
      } catch(e) {
        return [];
      }
    },

    changeSelectedLote() {
      this.formLote.loteId = Number(this.formLote.loteId);
      const lote = this.currentLote();
      if (!lote) {
        this.formLote.numeroLote = '';
        this.formLote.proveedor = '';
        this.formLote.precio = 0;
        this.formLote.cantidad = 0;
        this.formLote.fechaVencimiento = '';
        return;
      }
      this.formLote.numeroLote = lote.numeroLote;
      this.formLote.proveedor = lote.proveedor;
      this.formLote.precio = Number(lote.precio);
      this.formLote.cantidad = Number(lote.cantidad);
      this.formLote.fechaVencimiento = this.normalizeDateForInput(lote.fechaVencimiento || '');
      this.errorPrecioLote = ''; this.errorCantidadLote = ''; this.errorFechaLote = ''; this.errorProveedorLote = '';
    },

    validarLote() {
      var ok = true;
      this.errorProveedorLote = '';
      var locked = this.formLote.modo === 'edit' && this.currentLoteIsLocked();

      if (!locked) {
        var precio = Number(this.formLote.precio);
        if (!this.formLote.precio || isNaN(precio) || precio <= 0) {
          this.errorPrecioLote = 'Ingresa un precio valido mayor a 0.'; ok = false;
        } else { this.errorPrecioLote = ''; }

        var cantidad = Number(this.formLote.cantidad);
        if (!this.formLote.cantidad || isNaN(cantidad) || cantidad <= 0) {
          this.errorCantidadLote = 'Ingresa una cantidad valida mayor a 0.'; ok = false;
        } else { this.errorCantidadLote = ''; }
      } else {
        this.errorPrecioLote = '';
        this.errorCantidadLote = '';
      }

      if (!this.formLote.fechaVencimiento || this.formLote.fechaVencimiento.trim() === '') {
        this.errorFechaLote = 'La fecha de vencimiento es obligatoria.'; ok = false;
      } else {
        this.errorFechaLote = '';
      }

      return ok;
    },

    guardarLote() {
      if (!this.validarLote()) return;
      if (this.formLote.modo === 'edit') {
        if (!this.formLote.loteId) {
          SwalError('Error', 'No se seleccionó un lote para editar');
          return;
        }
        if (this.currentLoteIsLocked()) {
          if (!a11yNotify('error', 'Este lote está bloqueado y no puede editarse')) SwalError('Error', 'Este lote está bloqueado y no puede editarse');
          return;
        }
      }
      if (!this.beginAction('guardarLote')) return;
      if (this.formLote.modo === 'edit') {
        const url = API.DASHBOARD_PRODUCTO_LOTE(this.formLote.productoId, this.formLote.loteId);
        apiFetch(url, {
          method: 'PUT', body: this.formLote
        }).then(d => {
          if (d.success) {
            this.loadProductos();
            this.showModalRegistrarLote = false;
            if (!a11yNotify('success', 'Lote actualizado')) SwalSuccess('Lote actualizado');
          } else {
            const msg = d.error || 'No se pudo actualizar el lote';
            if (!a11yNotify('error', msg)) SwalError('Error', msg);
          }
        }).catch(() => { if (!a11yNotify('error', 'Error', 'No se pudo actualizar el lote')) SwalError('Error', 'No se pudo actualizar el lote'); })
          .finally(() => this.endAction('guardarLote'));
      } else {
        apiFetch(API.DASHBOARD_PRODUCTO_LOTES(this.formLote.productoId), {
          method: 'POST', body: this.formLote
        }).then(d => {
          if (d.success) {
            this.loadProductos();
            this.showModalRegistrarLote = false;
            if (!a11yNotify('success', 'Lote registrado')) SwalSuccess('Lote registrado');
          }
        }).catch(() => { if (!a11yNotify('error', 'Error', 'No se pudo registrar el lote')) SwalError('Error', 'No se pudo registrar el lote'); })
          .finally(() => this.endAction('guardarLote'));
      }
    },

    verGasto(gasto) { this.gastoVer = gasto; this.showModalVerGasto = true; },
    editarGasto(gasto) {
      const partes = gasto.fecha ? gasto.fecha.split('/') : [];
      const fechaEdit = partes.length === 3 ? `${partes[2]}-${partes[1]}-${partes[0]}` : '';
      this.formGasto = { ...gasto, fecha: fechaEdit, comprobanteFile: null, comprobantePreview: gasto.comprobante_url || null, _comprobanteUrl: gasto.comprobante_url || null, comprobanteClear: false };
      this.errorConceptoGasto = ''; this.errorTipoGasto = ''; this.errorMontoGasto = ''; this.errorFechaGasto = '';
      this.showModalAgregarGasto = true;
    },
    handleGastoComprobante(event) {
      const file = event.target.files[0];
      if (file) {
        this.formGasto.comprobanteFile = file;
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = e => { this.formGasto.comprobantePreview = e.target.result; };
          reader.readAsDataURL(file);
        } else { this.formGasto.comprobantePreview = 'file'; }
      }
    },
    confirmarEliminarGasto(gasto) { this.gastoEliminar = gasto; this.showModalConfirmarEliminarGasto = true; },
    eliminarGasto() {
      if (!this.gastoEliminar || !this.beginAction('eliminarGasto')) return;
      apiFetch(API.DASHBOARD_GASTO(this.gastoEliminar.id), { method: 'DELETE' }).then(() => {
        this.gastos = this.gastos.filter(g => g.id !== this.gastoEliminar.id);
        this.showModalConfirmarEliminarGasto = false;
        this._notify('Gasto eliminado');
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => this.endAction('eliminarGasto'));
    },
    validarGasto() {
      var ok = true;
      if (!this.formGasto.concepto || this.formGasto.concepto.trim() === '') {
        this.errorConceptoGasto = 'El concepto es obligatorio.'; ok = false;
      } else if (this.formGasto.concepto.trim().length < 2) {
        this.errorConceptoGasto = 'Minimo 2 caracteres.'; ok = false;
      } else { this.errorConceptoGasto = ''; }

      if (!this.formGasto.tipo || this.formGasto.tipo.trim() === '') {
        this.errorTipoGasto = 'Selecciona un tipo.'; ok = false;
      } else { this.errorTipoGasto = ''; }

      var monto = Number(this.formGasto.monto);
      if (!this.formGasto.monto || isNaN(monto) || monto <= 0) {
        this.errorMontoGasto = 'Ingresa un monto valido mayor a 0.'; ok = false;
      } else { this.errorMontoGasto = ''; }

      if (!this.formGasto.fecha || this.formGasto.fecha.trim() === '') {
        this.errorFechaGasto = 'La fecha es obligatoria.'; ok = false;
      } else { this.errorFechaGasto = ''; }

      return ok;
    },

    guardarGasto() {
      if (!this.validarGasto() || !this.beginAction('guardarGasto')) return;
      const isEdit = !!this.formGasto.id;
      const url = isEdit ? API.DASHBOARD_GASTO(this.formGasto.id) : API.DASHBOARD_GASTOS;
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
      const form = new FormData();
      for (const k in this.formGasto) {
        if (this.formGasto.hasOwnProperty(k) && k !== 'comprobanteFile' && k !== 'comprobantePreview' && k !== '_comprobanteUrl' && k !== 'comprobanteClear' && k !== 'comprobante_nombre') {
          form.append(k, this.formGasto[k]);
        }
      }
      if (this.formGasto.comprobanteFile) form.append('comprobante', this.formGasto.comprobanteFile);
      if (this.formGasto.comprobanteClear) form.append('comprobante_clear', 'true');
      fetch(url, { method: 'POST', body: form, headers: { 'X-CSRFToken': csrf } }).then(r => r.json()).then(d => {
        if (d && d.success === false) throw new Error(d.error || 'No se pudo guardar el gasto.');
        this.loadGastos();
        this.showModalAgregarGasto = false;
        this._notify(isEdit ? 'Gasto actualizado' : 'Gasto creado');
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => this.endAction('guardarGasto'));
    },
    resetFormGasto() { this.formGasto = { id: null, concepto: '', tipo: 'Variable', monto: 0, fecha: '', descripcion: '', comprobanteFile: null, comprobantePreview: null }; this.errorConceptoGasto = ''; this.errorTipoGasto = ''; this.errorMontoGasto = ''; this.errorFechaGasto = ''; },

    generarReporteGastos() {
      const gastosFiltrados = this.getGastosFiltradas();
      if (gastosFiltrados.length === 0) {
        if (!a11yNotify('warning', 'No hay gastos para generar el reporte')) SwalWarning('No hay gastos para generar el reporte');
        return;
      }

      const totalGeneral = gastosFiltrados.reduce((s, g) => s + g.monto, 0);
      const porTipo = {};
      gastosFiltrados.forEach(g => {
        if (!porTipo[g.tipo]) porTipo[g.tipo] = { cantidad: 0, total: 0 };
        porTipo[g.tipo].cantidad++;
        porTipo[g.tipo].total += g.monto;
      });

      let html = `
        <!DOCTYPE html>
        <html lang="es">
        <head>
          <meta charset="UTF-8">
          <title>Reporte de Gastos</title>
          <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #333; }
            h1 { color: #1e40af; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
            .info { margin-bottom: 20px; color: #555; font-size: 14px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th { background: #1e40af; color: white; padding: 12px 8px; text-align: left; font-size: 13px; }
            td { padding: 10px 8px; border-bottom: 1px solid #e5e7eb; font-size: 13px; }
            tr:nth-child(even) { background: #f8fafc; }
            .total-row { background: #dbeafe !important; font-weight: bold; }
            .resumen { margin-top: 30px; }
            .resumen h3 { color: #1e40af; margin-bottom: 10px; }
            .resumen-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #cbd5e1; }
            .gran-total { font-size: 18px; color: #1e40af; font-weight: bold; margin-top: 15px; padding-top: 10px; border-top: 2px solid #3b82f6; }
            @media print { body { padding: 20px; } }
          </style>
        </head>
        <body>
          <h1>Reporte de Gastos</h1>
          <div class="info">
            <p><strong>Fecha de generacion:</strong> ${new Date().toLocaleDateString('es-PE', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
            <p><strong>Total de registros:</strong> ${gastosFiltrados.length}</p>
          </div>

          <div class="resumen">
            <h3>Resumen por Tipo</h3>
            ${Object.keys(porTipo).map(tipo => `
              <div class="resumen-item">
                <span>${tipo} (${porTipo[tipo].cantidad} registros)</span>
                <span>S/ ${porTipo[tipo].total.toFixed(2)}</span>
              </div>
            `).join('')}
            <div class="resumen-item gran-total">
              <span>TOTAL GENERAL</span>
              <span>S/ ${totalGeneral.toFixed(2)}</span>
            </div>
          </div>

          <h3 style="margin-top:30px; color:#1e40af;">Detalle de Gastos</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Concepto</th>
                <th>Tipo</th>
                <th>Monto</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              ${gastosFiltrados.map(g => `
                <tr>
                  <td>GAS-${String(g.id).padStart(4, '0')}</td>
                  <td>${g.concepto}</td>
                  <td>${g.tipo}</td>
                  <td>S/ ${g.monto.toFixed(2)}</td>
                  <td>${g.fecha}</td>
                </tr>
              `).join('')}
              <tr class="total-row">
                <td colspan="3">TOTAL</td>
                <td>S/ ${totalGeneral.toFixed(2)}</td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </body>
        </html>
      `;

      const ventana = window.open('', '_blank');
      ventana.document.write(html);
      ventana.document.close();
      ventana.print();
    },

    verUsuario(usuario) { this.usuarioVer = usuario; this.showModalVerUsuario = true; },
    editarUsuario(usuario) { this.usuarioEditar = { ...usuario }; this.errorTelefonoEditar = ''; this.errorNombreEditar = ''; this.errorApellidoEditar = ''; this.errorUsernameEditar = ''; this.errorEmailEditar = ''; this.showModalEditarUsuario = true; },

    formTelefonoFormat(val) {
      if (!val) return '+51 ';
      var prefix = '+51 ';
      var numberPart = val.indexOf(prefix) === 0 ? val.slice(prefix.length) : val;
      var filtered = prefix;
      var digitCount = 0;
      for (var i = 0; i < numberPart.length; i++) {
        var ch = numberPart[i];
        if (/\d/.test(ch)) { if (digitCount >= 9) continue; digitCount++; }
        if (/\d/.test(ch) || ch === ' ') filtered += ch;
      }
      if (filtered.indexOf('+51') !== 0) filtered = prefix + filtered.replace(/^\+?\d*\s*/, '');
      return filtered;
    },

    validarTelefonoAdmin(tipo) {
      var val = tipo === 'crear' ? this.formNuevoUsuario.telefono : this.usuarioEditar.telefono;
      var errKey = tipo === 'crear' ? 'errorTelefonoCrear' : 'errorTelefonoEditar';
      if (!val || val.trim() === '' || val.trim() === '+51') { this[errKey] = ''; return true; }
      var v = val.replace(/^\+51\s*/, '');
      var errors = [];
      if (/[a-zA-Z]/.test(v)) errors.push('no se permiten letras');
      if (/[^0-9\s]/.test(v)) errors.push('caracteres no validos');
      var digits = v.replace(/\D/g, '');
      if (digits.length > 0 && digits.length < 7) errors.push('demasiado corto');
      if (digits.length > 0 && digits.length > 9) errors.push('maximo 9 digitos');
      if (errors.length > 0) { this[errKey] = errors.join(', ') + '.'; return false; }
      this[errKey] = '';
      return true;
    },

    formFiltrarNombre(val) {
      if (!val) return '';
      return val.replace(/[^a-zA-ZaeiouAEIOU\u00f1\u00d1\u00fc\u00dc\s]/g, '');
    },

    formFiltrarUsername(val) {
      if (!val) return '';
      return val.replace(/[^a-zA-Z0-9._]/g, '');
    },

    formFiltrarConcepto(val) {
      if (!val) return '';
      return val.replace(/[^a-zA-ZaeiouAEIOU\u00f1\u00d1\u00fc\u00dc\s]/g, '');
    },

    validarNombre(campo, tipo) {
      var val = tipo === 'crear' ? (campo === 'nombre' ? this.formNuevoUsuario.nombre : this.formNuevoUsuario.apellido) : (campo === 'nombre' ? this.usuarioEditar.nombre : this.usuarioEditar.apellido);
      var errKey = tipo === 'crear' ? (campo === 'nombre' ? 'errorNombreCrear' : 'errorApellidoCrear') : (campo === 'nombre' ? 'errorNombreEditar' : 'errorApellidoEditar');
      var label = campo === 'nombre' ? 'Nombre' : 'Apellido';
      if (!val || val.trim() === '') { this[errKey] = label + ' es obligatorio.'; return false; }
      var errors = [];
      if (/\d/.test(val)) errors.push('no se permiten numeros');
      if (/[^a-zA-ZaeiouAEIOU\u00f1\u00d1\u00fc\u00dc\s]/.test(val)) errors.push('no se permiten caracteres especiales');
      if (val.trim().length < 2) errors.push('minimo 2 caracteres');
      if (errors.length > 0) { this[errKey] = errors.join(', ') + '.'; return false; }
      this[errKey] = '';
      return true;
    },

    validarUsernameAdmin(tipo) {
      var val = tipo === 'crear' ? this.formNuevoUsuario.username : this.usuarioEditar.username;
      var errKey = tipo === 'crear' ? 'errorUsernameCrear' : 'errorUsernameEditar';
      if (!val || val.trim() === '') { this[errKey] = 'El nombre de usuario es obligatorio.'; return false; }
      var errors = [];
      if (/^[0-9]/.test(val)) errors.push('no puede comenzar con un numero');
      if (!/[A-Z]/.test(val)) errors.push('falta al menos una mayuscula');
      if (!/[0-9]/.test(val)) errors.push('falta al menos un numero');
      if (/[^a-zA-Z0-9._]/.test(val)) errors.push('solo letras, numeros, puntos y guiones bajos');
      if (val.length < 6) errors.push('minimo 6 caracteres');
      if (errors.length > 0) { this[errKey] = errors.join(', ') + '.'; return false; }
      this[errKey] = '';
      return true;
    },

    validarEmailAdmin(tipo) {
      var val = tipo === 'crear' ? this.formNuevoUsuario.email : this.usuarioEditar.email;
      var errKey = tipo === 'crear' ? 'errorEmailCrear' : 'errorEmailEditar';
      var dominiosValidos = ['gmail.com', 'outlook.com', 'hotmail.com', 'live.com', 'msn.com', 'unitru.edu.pe'];
      if (!val || val.trim() === '') { this[errKey] = 'El correo es obligatorio.'; return false; }
      var a = val.indexOf('@');
      if (a === -1) { this[errKey] = 'Falta el simbolo "@" en el correo.'; return false; }
      var local = val.substring(0, a);
      var domain = val.substring(a + 1);
      if (!local) { this[errKey] = 'Falta el nombre de usuario antes del "@".'; return false; }
      if (!domain) { this[errKey] = 'Falta el dominio. Usa: ' + dominiosValidos.join(', ') + '.'; return false; }
      if (domain.indexOf('.') === -1) { this[errKey] = 'Dominio no valido. Usa: ' + dominiosValidos.join(', ') + '.'; return false; }
      var parts = domain.split('.');
      var tld = parts[parts.length - 1];
      if (tld.length < 2) { this[errKey] = 'Extension del dominio no valida. Usa: ' + dominiosValidos.join(', ') + '.'; return false; }
      var typoMap = { 'con': 'com', 'cmo': 'com', 'ocm': 'com', 'ne': 'net', 'ogr': 'org' };
      if (typoMap[tld]) { this[errKey] = '¿Quizas quisiste decir ".' + typoMap[tld] + '"? Escribiste ".' + tld + '".'; return false; }
      if (!/^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+$/.test(local)) { this[errKey] = 'El nombre de usuario contiene caracteres no validos.'; return false; }
      var domainLower = domain.toLowerCase();
      if (dominiosValidos.indexOf(domainLower) === -1) { this[errKey] = 'Dominio no valido. Usa: ' + dominiosValidos.join(', ') + '.'; return false; }
      this[errKey] = '';
      return true;
    },

    validarCamposUsuario(tipo) {
      var ok = true;
      if (!this.validarNombre('nombre', tipo)) ok = false;
      if (!this.validarNombre('apellido', tipo)) ok = false;
      if (!this.validarUsernameAdmin(tipo)) ok = false;
      if (!this.validarEmailAdmin(tipo)) ok = false;
      if (!this.validarTelefonoAdmin(tipo)) ok = false;
      return ok;
    },

    guardarUsuario() {
      if (!this.validarCamposUsuario('editar') || !this.beginAction('guardarUsuario')) return;
      var bodyEditar = { ...this.usuarioEditar };
      if (bodyEditar.telefono && bodyEditar.telefono.replace(/\+51\s*/, '').trim() === '') bodyEditar.telefono = '';
      apiFetch(API.DASHBOARD_USUARIO(this.usuarioEditar.id), {
        method: 'PUT', body: bodyEditar
      }).then(d => {
        if (d && d.success === false) throw new Error(d.error || 'No se pudo actualizar el usuario');
        this.loadUsuarios();
        this.showModalEditarUsuario = false;
        this._notify('Usuario actualizado');
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => this.endAction('guardarUsuario'));
    },
    restablecerContrasena() {
      this.showModalResetPassword = true;
    },
    confirmarResetPassword() {
      if (!this.beginAction('resetPassword')) return;
      apiFetch(API.DASHBOARD_USUARIO_RESET(this.usuarioEditar.id), { method: 'POST' }).then(d => {
        if (d && d.success) {
          this.showModalResetPassword = false;
          if (!a11yNotify('success', 'Contraseña restablecida', 'La nueva contraseña es: Cambiar123++')) SwalSuccess('Contraseña restablecida', 'La nueva contraseña es: Cambiar123++');
        } else { if (!a11yNotify('error', 'Error', 'No se pudo restablecer la contraseña')) SwalError('Error', 'No se pudo restablecer la contraseña'); }
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => this.endAction('resetPassword'));
    },
    desactivarUsuario(usuario) { this.usuarioDesactivar = usuario; this.showModalConfirmarDesactivar = true; },
    toggleUsuarioEstado() {
      if (!this.usuarioDesactivar || !this.beginAction('toggleUsuario')) return;
      apiFetch(API.DASHBOARD_USUARIO_TOGGLE(this.usuarioDesactivar.id), { method: 'POST' }).then(d => {
        if (d.success) { this.usuarioDesactivar.activo = d.activo; this.showModalConfirmarDesactivar = false; this._notify('Estado de usuario actualizado'); }
        else throw new Error(d.error || 'No se pudo actualizar el usuario.');
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => this.endAction('toggleUsuario'));
    },

    crearUsuario() {
      if (this.loadingCrearUsuario || !this.validarCamposUsuario('crear')) return;
      this.loadingCrearUsuario = true;
      var bodyCrear = { ...this.formNuevoUsuario };
      if (bodyCrear.telefono && bodyCrear.telefono.replace(/\+51\s*/, '').trim() === '') bodyCrear.telefono = '';
      apiFetch(API.DASHBOARD_USUARIOS, { method: 'POST', body: bodyCrear }).then(d => {
        if (d.success) {
          this.formNuevoUsuario = { nombre: '', apellido: '', email: '', telefono: '', rol: 'employee', username: '' };
          this.errorTelefonoCrear = '';
          this.showModalCrearTrabajador = false;
          this.loadUsuarios();
          if (!a11yNotify('success', 'Usuario creado', 'Contraseña inicial: Cambiar123++')) SwalSuccess('Usuario creado', 'Contraseña inicial: Cambiar123++');
        } else { if (!a11yNotify('error', 'Error', d.error || 'No se pudo crear el usuario')) SwalError('Error', d.error || 'No se pudo crear el usuario'); }
      }).catch(() => { if (!a11yNotify('error', 'Error de conexión', 'Intenta de nuevo.')) SwalError('Error de conexión', 'Intenta de nuevo.'); })
        .finally(() => { this.loadingCrearUsuario = false; });
    },

    agregarAlCarrito(prod) {
      const precio = this.productoPrecio(prod);
      const existing = this.carrito.find(c => c.id === prod.id);
      if (existing) { existing.cantidad++; }
      else { this.carrito.push({ id: prod.id, nombre: prod.nombre, precio: precio, cantidad: 1, imagen: prod.imagen || null, color: prod.color, icono: prod.icono }); }
    },
    abrirModalPago() {
      this.montoRecibido = 0; this.metodoPago = 'Efectivo'; this.pagoStep = 1;
      this.pagoQRB64 = ''; this.pagoSimulationUrl = ''; this.pagoOrderId = null; this.pagoBoletaCode = '';
      this.showModalPago = true;
    },
    procesarPago() {
      if ((this.metodoPago === 'Efectivo' && this.montoRecibido < this.ventaTotal) || !this.beginAction('procesarPago')) return;
      apiFetch(API.DASHBOARD_VENTAS, {
        method: 'POST', body: { items: this.carrito, metodo: this.metodoPago }
      }).then(d => {
        if (d.success) {
          if (d.pending_payment) {
            this.pagoOrderId = d.id; this.pagoBoletaCode = d.boleta_code || '';
            this.pagoQRB64 = d.simulation_qr_b64 || ''; this.pagoSimulationUrl = d.simulation_url || '';
            this.pagoStep = 2;
            this.startPagoPolling();
          } else {
            const total = this.ventaTotal;
            const metodo = this.metodoPago;
            this.carrito = []; this.montoRecibido = 0; this.metodoPago = 'Efectivo';
            this.showModalPago = false; this.showModalBoleta = true;
            this.boletaVenta = { id: d.id, boleta_code: d.boleta_code || '', cliente: 'Cliente Mostrador', total: total, metodo: metodo };
            this.refreshVentas();
          }
        } else {
          throw new Error(d.error || 'No se pudo registrar la venta.');
        }
      }).catch(error => {
        if (!a11yNotify('error', 'Error', error.message)) SwalError('Error', error.message);
      }).finally(() => this.endAction('procesarPago'));
    },
    startPagoPolling() {
      this.pagoPolling = usePolling(() => {
        apiFetch(API.PAYMENT_CHECK(this.pagoOrderId)).then(data => {
          if (data.is_paid) {
            this.pagoPolling.stop();
            apiFetch(API.DASHBOARD_VENTA_COMPLETAR(this.pagoOrderId), { method: 'POST' }).then(() => {
              this.pagoStep = 3;
              return this.refreshVentas();
            });
          }
        });
      });
      this.pagoPolling.start();
    },
    stopPagoPolling() { if (this.pagoPolling) this.pagoPolling.stop(); },
    cancelarPago() {
      this.stopPagoPolling();
      apiFetch(API.ORDER_CANCEL_UNPAID(this.pagoOrderId), { method: 'POST', body: {} })
        .then(() => { this.pagoStep = 1; this.showModalPago = false; })
        .catch(() => { this.pagoStep = 1; this.showModalPago = false; });
    },
    cerrarPagoExitoso() {
      const metodo = this.metodoPago; const orderId = this.pagoOrderId;
      const total = this.ventaTotal; const boletaCode = this.pagoBoletaCode;
      this.stopPagoPolling();
      this.carrito = []; this.montoRecibido = 0; this.metodoPago = 'Efectivo';
      this.pagoStep = 1; this.pagoQRB64 = ''; this.pagoSimulationUrl = '';
      this.pagoOrderId = null; this.pagoBoletaCode = '';
      this.showModalPago = false;
      this.boletaVenta = { id: orderId, boleta_code: boletaCode, cliente: 'Cliente Mostrador', total: total, metodo: metodo };
      this.showModalBoleta = true;
      this.refreshVentas();
    },

    verGuia(tipo) {
      const guias = {
        inventario: {
          titulo: 'Guia: Gestion de Inventario',
          pasos: [
            'Ingrese a la seccion Inventario desde el menu lateral.',
            'Use el buscador o filtro de categoria para encontrar productos.',
            'Para agregar un producto, haga clic en "Agregar Producto" y complete los datos.',
            'El codigo de barras se genera automaticamente al guardar.',
            'Para registrar un lote, haga clic en el icono de lote (+) en cada producto.',
            'Los productos con stock bajo el umbral se marcan en rojo automaticamente.',
            'Use Ctrl+K para buscar rapidamente desde cualquier seccion.'
          ]
        },
        ventas: {
          titulo: 'Guia: Gestion de Pedidos Online',
          pasos: [
            'Ingrese a la seccion Ventas y seleccione la pestana "Pedidos Online".',
            'Los pedidos nuevos aparecen con estado "Pendiente".',
            'Para preparar un pedido, haga clic en el boton de preparar.',
            'Marque como "Listo para entrega" cuando este listo.',
            'Use el escaner QR para confirmar entregas con el codigo del cliente.',
            'Puede validar codigos de boleta manualmente si es necesario.',
            'Los pedidos completados se registran automaticamente como ventas.'
          ]
        },
        'venta-manual': {
          titulo: 'Guia: Venta Manual',
          pasos: [
            'En la seccion Ventas, asegurese de tener la pestana "Venta Manual" activa (resaltada en verde).',
            'En el panel izquierdo, busque productos escribiendo su nombre o codigo de barras.',
            'Haga clic sobre un producto para agregarlo al carrito de venta (seccion derecha).',
            'En el carrito puede modificar la cantidad con los botones +/- o eliminar items.',
            'Seleccione el metodo de pago: Efectivo, Yape, Plin o Transferencia.',
            'Si elige Yape, seleccione el tipo: codigo generado o numero de telefono.',
            'Para pagos con transferencia, elija el banco: BCP, Interbank, BBVA o Scotiabank.',
            'En efectivo, ingrese el monto con el que paga el cliente; el vuelto se calcula solo.',
            'Confirme la venta con el boton "Procesar Pago" para emitir la boleta.',
            'Si el pago es electronico, se abrira una ventana de simulacion; siga las instrucciones.',
            'Finalmente, puede imprimir la boleta desde el modal de confirmacion.'
          ]
        },
        'lista-ventas': {
          titulo: 'Guia: Lista de Ventas',
          pasos: [
            'Cambie a la pestana "Lista de Ventas" dentro de la seccion Ventas.',
            'La tabla muestra todas las ventas registradas con su numero, cliente, total y estado.',
            'Use los filtros superiores: busqueda por ID o boleta, fecha especifica, canal (Online/Presencial) y trabajador.',
            'Los estados de venta incluyen: Completado, Listo para entrega y Cancelado.',
            'Haga clic en el icono de ojo para ver el detalle completo de una venta.',
            'En el detalle puede ver los items, metodo de pago, y el trabajador que la atendio.',
            'Use el icono de impresora para ver e imprimir la boleta de la venta.',
            'Para ventas online, puede ver quien valido la entrega en el campo "Validado por".',
            'El boton de exportar permite descargar el listado completo en PDF o Excel.',
            'La paginacion en la parte inferior permite navegar entre paginas de resultados.'
          ]
        },
        gastos: {
          titulo: 'Guia: Control de Gastos',
          pasos: [
            'Ingrese a la seccion Gastos desde el menu lateral.',
            'Haga clic en "Registrar Gasto" para crear uno nuevo.',
            'Seleccione el tipo: Fijo, Variable, Operativo o Mantenimiento.',
            'Ingrese el monto, fecha y descripcion del gasto.',
            'Opcionalmente adjunte un comprobante (imagen o PDF).',
            'Para editar, haga clic en el icono de lapiz en la tabla.',
            'Los gastos se reflejan automaticamente en los reportes.'
          ]
        },
        reportes: {
          titulo: 'Guia: Reportes y Analisis',
          pasos: [
            'Ingrese a la seccion Reportes desde el menu lateral.',
            'Seleccione el sub-view: Ventas, Gastos o Dashboard.',
            'Use los filtros de fecha para ajustar el periodo de analisis.',
            'Exporte reportes en PDF o Excel con los botones correspondientes.',
            'El dashboard muestra metricas clave: ventas semana, gastos mes, utilidad.',
            'Los graficos muestran tendencias de ventas y comparativas.'
          ]
        },
        usuarios: {
          titulo: 'Guia: Gestion de Usuarios',
          pasos: [
            'Ingrese a la seccion Usuarios desde el menu lateral.',
            'Use las pestanas para filtrar: Todos, Empleados, Clientes.',
            'Para crear un empleado, haga clic en "Registrar Usuario".',
            'La contrasena inicial es "Cambiar123++" (el usuario debera cambiarla).',
            'Para editar un usuario, haga clic en el icono de lapiz.',
            'Para desactivar, use el icono de energia (no se elimina el registro).',
            'Use el buscador para encontrar usuarios por nombre o email.'
          ]
        },
        general: {
          titulo: 'Guia General del Sistema',
          pasos: [
            'El menu lateral le permite navegar entre las diferentes secciones.',
            'Use los atajos de teclado (Alt+1 a Alt+7) para navegacion rapida entre secciones.',
            'Ctrl+K abre la busqueda rapida de productos.',
            'Las notificaciones (campana) muestran pedidos online pendientes.',
            'Su perfil se muestra en la parte inferior del sidebar.',
            'Los filtros y busquedas estan disponibles en cada seccion.',
            'La paginacion le permite navegar entre registros.'
          ]
        }
      };
      const guia = guias[tipo] || guias.general;
      this.guiaTitulo = guia.titulo;
      this.guiaPasos = guia.pasos;
      this.showModalGuia = true;
    },

    getVentasFiltradas() {
      return this.ventas.filter(v => {
        const matchId = !this.busquedaVentaId ||
          String(v.id).includes(this.busquedaVentaId) ||
          (v.boleta_code && v.boleta_code.toLowerCase().includes(this.busquedaVentaId.toLowerCase()));
        const matchCanal = !this.filtroCanalVenta || v.canal === this.filtroCanalVenta;
        const matchTrabajador = !this.filtroTrabajadorVenta || v.trabajador === this.filtroTrabajadorVenta;
        let matchFecha = true;
        if (this.filtroFechaVenta) {
          const parts = v.fecha.split('/');
          const apiFecha = parts[2] + '-' + parts[1] + '-' + parts[0];
          matchFecha = apiFecha === this.filtroFechaVenta;
        }
        return matchId && matchCanal && matchTrabajador && matchFecha;
      });
    },

    get ventasPg() { return this.paginatedItems(this.getVentasFiltradas(), this.ventasPage); },
    get invPg() { return this.paginatedItems(this.filteredInventario, this.invPage); },
    get gastosPg() { return this.paginatedItems(this.getGastosFiltradas(), this.gastosPage); },
    get usuariosPg() { return this.paginatedItems(this.filteredUsuarios, this.usuariosPage); },
    get topProdPg() { return this.paginatedItems(this.topProductos, this.topProdPage); },
    get stockPg() { return this.paginatedItems(this.productos, this.stockPage); },
    get filteredStockBajo() { return this.productos.filter(p => this.productoStock(p) < p.umbral); },
    get stockBajoPg() { return this.paginatedItems(this.filteredStockBajo, this.stockBajoPage); },

    adminOrderBadgeClass,
    adminVentaBadgeClass,
    statusIcon,
    paymentLabel,
    paymentBadgeClass,
    getVentasTotales() { return this.ventas.reduce((s, v) => s + v.total, 0); },
    getGastosFiltradas() {
      return this.gastos.filter(g => {
        const matchBusqueda = !this.busquedaGasto ||
          String(g.id).includes(this.busquedaGasto) ||
          ('GAS-' + String(g.id).padStart(4, '0')).toLowerCase().includes(this.busquedaGasto.toLowerCase()) ||
          g.concepto.toLowerCase().includes(this.busquedaGasto.toLowerCase());
        const matchTipo = !this.filtroTipoGasto || g.tipo === this.filtroTipoGasto;
        let matchFecha = true;
        if (this.filtroFechaGasto) {
          const parts = g.fecha.split('/');
          const apiFecha = parts[2] + '-' + parts[1] + '-' + parts[0];
          matchFecha = apiFecha === this.filtroFechaGasto;
        }
        return matchBusqueda && matchTipo && matchFecha;
      });
    },

    getGastosTotales() { return this.gastos.reduce((s, g) => s + g.monto, 0); },
    getUtilidadNeta() { return this.getVentasTotales() - this.getGastosTotales(); },
    getTicketPromedio() { return this.ventas.length ? this.getVentasTotales() / this.ventas.length : 0; },
    getStockTotal() { return this.productos.reduce((s, p) => s + this.productoStock(p), 0); },
    getStockBajoCount() { return this.productos.filter(p => this.productoStock(p) < p.umbral).length; },
    getValorInventario() { return this.productos.reduce((s, p) => s + this.productoStock(p) * this.productoPrecio(p), 0); },

    abrirExportar(tipo, titulo) { this.exportarFormato = ''; this.exportarTitulo = titulo; this.exportarRangoFecha = { inicio: '', fin: '' }; this.showModalExportar = true; },
    seleccionarFormato(formato) { this.exportarFormato = formato; },
    confirmarExportar() {
      if (!this.exportarFormato) return;
      this._notify('Reporte exportado en ' + this.exportarFormato.toUpperCase());
      this.showModalExportar = false;
    }
  };
}
