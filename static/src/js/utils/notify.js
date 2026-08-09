import Alpine from 'alpinejs';

export function a11yNotify(type, title, description = '') {
  const a11y = Alpine.store('a11y');
  if (a11y?.hearing) {
    a11y.showToast(type, title, description);
    return true;
  }
  return false;
}
