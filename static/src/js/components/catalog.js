import { apiFetch } from '../services/api.js';
import { SwalToast } from '../utils/swal.js';
import { API } from '../services/urls.js';
import { a11yNotify } from '../utils/notify.js';

export function catalogApp(initialState = {}) {
  return {
    products: [],
    search: initialState.search || '',
    category: initialState.category || '',
    categoryName: '',
    categories: [],
    loading: true,
    currentPage: initialState.page || 1,
    totalPages: 1,

    initCatalog() {
      const params = new URLSearchParams(window.location.search);
      const cat = params.get('category') || this.category;
      const search = params.get('q') || params.get('search') || this.search;
      const page = parseInt(params.get('page') || this.currentPage, 10);
      this.category = cat || '';
      this.search = search || this.search;
      this.currentPage = page > 0 ? page : 1;
      this.loadProducts();
    },

    loadProducts() {
      this.loading = true;
      if (this.category) {
        const matched = this.categories.find(c => c.slug === this.category);
        this.categoryName = matched ? matched.name : '';
      } else {
        this.categoryName = '';
      }
      let url = API.CATALOG_DATA;
      const params = [];
      if (this.search) params.push('q=' + encodeURIComponent(this.search));
      if (this.category) params.push('category=' + encodeURIComponent(this.category));
      if (this.currentPage > 1) params.push('page=' + encodeURIComponent(this.currentPage));
      if (params.length) url += '?' + params.join('&');
      apiFetch(url).then(d => {
        if (d.success) {
          this.products = d.products;
          this.categories = d.categories;
          this.currentPage = d.pagination?.current_page || 1;
          this.totalPages = d.pagination?.total_pages || 1;
        }
        if (this.category) {
          const matched = this.categories.find(c => c.slug === this.category);
          this.categoryName = matched ? matched.name : '';
        }
        this.loading = false;
      });
    },

    addToCart(productId) {
      apiFetch(API.CART_ADD, {
        method: 'POST',
        body: { product_id: productId, quantity: 1 }
      }).then(d => {
        if (d.success) {
          if (!a11yNotify('success', 'Producto agregado al carrito')) SwalToast('success', '¡Producto agregado al carrito!');
          window.dispatchEvent(new CustomEvent('ym:cartUpdated', { detail: { count: d.cart_count, showCart: true } }));
        }
      });
    },

    goToPage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.loadProducts();
      const params = new URLSearchParams(window.location.search);
      if (this.search) params.set('q', this.search);
      else params.delete('q');
      if (this.category) params.set('category', this.category);
      else params.delete('category');
      params.set('page', this.currentPage);
      const newUrl = window.location.pathname + '?' + params.toString();
      window.history.replaceState({}, '', newUrl);
    },

    clearFilters() {
      this.search = '';
      this.category = '';
      this.categoryName = '';
      this.currentPage = 1;
      window.history.replaceState({}, '', window.location.pathname);
      this.loadProducts();
    }
  };
}
