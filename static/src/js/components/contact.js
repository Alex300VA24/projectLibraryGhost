import { SwalSuccess, SwalError } from '../utils/swal.js';
import { a11yNotify } from '../utils/notify.js';

export function contactApp() {
  return {
    sent: false,
    form: { nombre: '', apellido: '', email: '', asunto: '', mensaje: '' },
    enviarMensaje() {
      if (!this.form.nombre || !this.form.email || !this.form.asunto || !this.form.mensaje) {
        if (!a11yNotify('warning', 'Campos incompletos', 'Por favor completa todos los campos obligatorios.')) Swal.fire({ icon: 'warning', title: 'Campos incompletos', text: 'Por favor completa todos los campos obligatorios.', confirmButtonColor: '#2563eb' });
        return;
      }
      if (!this.form.email.includes('@')) {
        if (!a11yNotify('error', 'Correo inválido', 'Ingresa un correo electrónico válido.')) Swal.fire({ icon: 'error', title: 'Correo inválido', text: 'Ingresa un correo electrónico válido.', confirmButtonColor: '#2563eb' });
        return;
      }
      if (this.form.mensaje.length < 10) {
        if (!a11yNotify('warning', 'Mensaje muy corto', 'El mensaje debe tener al menos 10 caracteres.')) Swal.fire({ icon: 'warning', title: 'Mensaje muy corto', text: 'El mensaje debe tener al menos 10 caracteres.', confirmButtonColor: '#2563eb' });
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
