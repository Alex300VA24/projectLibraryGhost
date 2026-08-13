import { SwalSuccess, SwalError, SwalWarning } from '../utils/swal.js';
import { a11yNotify } from '../utils/notify.js';

export function contactApp() {
  return {
    sent: false,
    form: { nombre: '', apellido: '', email: '', asunto: '', mensaje: '' },
    enviarMensaje() {
      if (!this.form.nombre || !this.form.email || !this.form.asunto || !this.form.mensaje) {
        if (!a11yNotify('warning', 'Campos incompletos', 'Por favor completa todos los campos obligatorios.')) SwalWarning('Campos incompletos', 'Por favor completa todos los campos obligatorios.');
        return;
      }
      if (!this.form.email.includes('@')) {
        if (!a11yNotify('error', 'Correo inválido', 'Ingresa un correo electrónico válido.')) SwalError('Correo inválido', 'Ingresa un correo electrónico válido.');
        return;
      }
      if (this.form.mensaje.length < 10) {
        if (!a11yNotify('warning', 'Mensaje muy corto', 'El mensaje debe tener al menos 10 caracteres.')) SwalWarning('Mensaje muy corto', 'El mensaje debe tener al menos 10 caracteres.');
        return;
      }
      this.sent = true;
      if (!a11yNotify('success', 'Mensaje enviado', 'Te responderemos pronto.')) SwalSuccess('¡Mensaje enviado!', 'Te responderemos pronto.');
    },
    resetForm() {
      this.sent = false;
      this.form = { nombre: '', apellido: '', email: '', asunto: '', mensaje: '' };
    }
  };
}
