# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Clientes de la librería**: Personas que navegan el catálogo, añaden productos al carrito, realizan pedidos con diferentes métodos de pago (Yape, Plin, transferencias) y reciben sus compras.
- **Administradores/empleados**: Personal que gestiona productos, pedidos, ventas, empleados, gastos y notificaciones desde un panel centralizado.

## Product Purpose

Sistema web de gestión de pedidos y ventas para una librería. Permite a los clientes comprar productos online con simulación de pagos locales, mientras los administradores gestionan el negocio desde un dashboard integral. El éxito se mide en eficiencia operativa, satisfacción del cliente y precisión en la gestión de inventario.

## Positioning

Soporte nativo para métodos de pago peruanos (Yape, Plin, transferencias BCP e Interbank) con simulación realista, combinado con un panel de administración completo y modos de accesibilidad especializados (daltónico y discapacidad auditiva) que otras soluciones no ofrecen de forma integrada.

## Operating Context

- **Flujo del cliente**: Navegar catálogo → añadir al carrito → checkout con método de pago → recibir confirmación y boleta
- **Flujo del admin**: Dashboard → gestión de productos/pedidos/ventas → notificaciones en tiempo real → generación de reportes
- **Entorno técnico**: Servidor Django con MySQL, frontend con Alpine.js y Tailwind CSS, compilación con esbuild/pnpm

## Capabilities and Constraints

- Catálogo de productos con búsqueda, filtros y vista detallada
- Carrito de compras persistente con sesión anónima y fusión al iniciar sesión
- Pedidos online con flujo Pendiente → Listo para entrega → Completado / Cancelado
- Simulación de pagos — Yape (QR + código de aprobación), Plin, Transferencia BCP e Interbank
- Panel de administración — Dashboard con gestión de productos, pedidos, ventas, empleados, gastos y notificaciones
- Boletas — Generación de boletas HTML y PDF con código QR para validación en caja
- Autenticación — Registro, inicio de sesión, recuperación de contraseña, perfiles con preferencias de accesibilidad
- Modo accesibilidad — Modo daltónico y modo para discapacidad auditiva
- Notificaciones en tiempo real y por correo electrónico
- Escáner de código de barras — API para integración con lectores externos

## Brand Commitments

- Nombre: Libreria Ghostitzer
- Licencia: Uso interno — Libreria Ghostitzer SAC

## Evidence on Hand

- Código fuente completo en Django con_APPS: accounts, orders, products
- Plantillas HTML con Alpine.js y Tailwind CSS
- Simulación de pagos en payment_simulation/
- Documentación en README.md con instrucciones de instalación y uso

## Product Principles

1. Experiencia de compra fluida y segura para clientes
2. Gestión eficiente y centralizada para administradores
3. Accesibilidad como estándar, no como complemento
4. Simulación de pagos realista para el contexto peruano
5. Mantenimiento y escalabilidad del código

## Accessibility & Inclusion

- Modo daltónico para usuarios con daltonismo
- Modo para discapacidad auditiva
- Preferencias de accesibilidad en perfiles de usuario