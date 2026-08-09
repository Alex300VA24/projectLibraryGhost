# 📚 Ghostitzer Library

Sistema web de gestión de una librería moderna, enfocado en la experiencia de compra de libros, cómics, materiales y productos de colección. Permite a los clientes navegar el catálogo, añadir artículos al carrito y descubrir una tienda con identidad propia inspirada en Ghostitzer.

---

## ✨ Funcionalidades

- **Catálogo de productos** con búsqueda, filtros y vista detallada.
- **Carrito de compras** persistente con sesión anónima y fusión al iniciar sesión.
- **Pedidos online** con flujo Pendiente → Listo para entrega → Completado / Cancelado.
- **Simulación de pagos** — Yape (QR + código de aprobación), Plin, Transferencia BCP e Interbank.
- **Panel de administración** — Dashboard con gestión de productos, pedidos, ventas, empleados, gastos y notificaciones.
- **Boletas** — Generación de boletas HTML y PDF con código QR para validación en caja.
- **Autenticación** — Registro, inicio de sesión, recuperación de contraseña, perfiles con preferencias de accesibilidad.
- **Modo accesibilidad** — Modo daltónico y modo para discapacidad auditiva.
- **Notificaciones** en tiempo real y por correo electrónico.
- **Escáner de código de barras** — API para integración con lectores externos.

---

## 🧱 Tecnologías

| Capa          | Tecnología                                    |
|---------------|-----------------------------------------------|
| Backend       | Python 3.10+, Django 6.0                      |
| Base de datos | MySQL 8+                                      |
| Frontend      | Alpine.js 3, Tailwind CSS 3, Font Awesome 7   |
| Build JS      | esbuild                                       |
| Paquetería    | pnpm (Node.js 18+)                            |
| PDF           | xhtml2pdf                                     |
| QR            | qrcode + python-barcode                       |

---

## 📋 Requisitos

- **Python** 3.10 o superior
- **MySQL** 8 o superior
- **Node.js** 18 o superior + **pnpm** (`npm install -g pnpm`)
- **Git**

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/library_ghostitzer.git
cd library_ghostitzer
```

### 2. Entorno virtual y dependencias Python

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux / macOS

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus datos (correo SMTP, IP, etc.)
```

### 4. Base de datos

Crea una base de datos MySQL:

```sql
CREATE DATABASE library_ghostitzer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Las credenciales están en `library_ghostitzer/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'library_ghostitzer_db',
        'USER': 'root',
        'PASSWORD': 'admin123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

> ⚠️ Cambia estos valores según tu configuración local.

### 5. Migraciones y datos iniciales

```bash
python manage.py migrate
python manage.py cargar_productos_ejemplo   # carga productos de ejemplo
python manage.py createsuperuser            # crea un usuario administrador
```

### 6. Dependencias frontend

```bash
pnpm install
```

### 7. Construir assets estáticos

```bash
pnpm run build
```

### 8. Archivos multimedia

Asegúrate de que exista el directorio `media/` y sus subdirectorios:

```bash
mkdir -p media/products media/comprobantes
```

### 9. Ejecutar el servidor

```bash
python manage.py runserver
```

Abre [http://localhost:8000](http://localhost:8000) en tu navegador.

---

## 🔧 Comandos útiles

| Comando                           | Descripción                                |
|-----------------------------------|--------------------------------------------|
| `python manage.py runserver`      | Inicia el servidor de desarrollo           |
| `pnpm run dev`                    | Compila Tailwind en modo watch             |
| `pnpm run dev:js`                 | Compila JS con esbuild en modo watch       |
| `pnpm run build`                  | Compila CSS y JS para producción           |
| `python manage.py migrate`        | Aplica migraciones                         |
| `python manage.py makemigrations` | Crea nuevas migraciones                    |
| `python manage.py shell`          | Consola interactiva de Django              |
| `python manage.py dumpdata`       | Exporta datos a JSON                       |

---

## 🗂️ Estructura del proyecto

```
library_ghostitzer/
├── manage.py
├── requirements.txt
├── package.json
├── tailwind.config.js
├── .env.example
├── library_ghostitzer/      # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── apps/
│   ├── accounts/             # Usuarios, autenticación, perfiles
│   ├── products/             # Catálogo, productos, lotes
│   └── orders/               # Carrito, pedidos, pagos, boletas
├── core/                     # Home, dashboard, admin API
├── payment_simulation/       # Simulación de pagos (Yape, Plin, BCP, Interbank)
├── templates/                # Plantillas Django globales
│   ├── accounts/
│   ├── core/                 # Incluye admin/partials/
│   ├── emails/
│   ├── orders/
│   └── registration/
├── static/
│   ├── src/                  # Fuentes (CSS, JS, imágenes)
│   │   ├── css/app.css       # Entrada Tailwind
│   │   └── js/app.js         # Entrada Alpine.js
│   └── dist/                 # Compilado (no tocar)
└── media/                    # Subidas por el usuario
```

---

## 📬 Email

El envío de correos (boletas, notificaciones, bienvenida) se configura en `.env` usando SMTP de Gmail.  
Se necesita una **contraseña de aplicación** de Google (no la contraseña normal).

---

## 🧪 Simulación de pagos

El sistema incluye páginas de simulación que imitan el flujo real de pagos:

- **Yape**: QR o código de aprobación de 6 dígitos.
- **Plin**: QR.
- **Transferencia BCP / Interbank**: Página con datos bancarios simulados.

Estas páginas están en `payment_simulation/` y se acceden desde la URL `/simulacion-pago/...`.

---

## 🤝 Contribuir

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit de tus cambios (`git commit -am 'Agrega nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

---

## 📄 Licencia

Uso interno — Libreria Ghostitzer SAC
