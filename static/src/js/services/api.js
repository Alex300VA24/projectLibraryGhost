let _csrfToken = '';

export function initCsrf() {
  _csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
}

export function getCsrf() {
  if (!_csrfToken) initCsrf();
  return _csrfToken;
}

export async function apiFetch(url, options = {}) {
  const headers = { 'X-CSRFToken': getCsrf() };

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  const response = await fetch(url, { ...options, headers, cache: 'no-store' });
  return response.json();
}
