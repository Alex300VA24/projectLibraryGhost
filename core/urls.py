from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('como-funciona/', views.como_funciona, name='como_funciona'),
    path('contacto/', views.contacto, name='contacto'),
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cuenta/', include('apps.accounts.urls')),
    path('catalogo/', include('apps.products.urls')),
    path('', include('apps.orders.urls')),
]

# Dashboard API endpoints
api_urlpatterns = [
    path('dashboard/api/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('dashboard/api/categorias/', views.api_categorias, name='api_categorias'),
    path('dashboard/api/productos/', views.api_productos, name='api_productos'),
    path('dashboard/api/productos/<int:producto_id>/', views.api_producto_detalle, name='api_producto_detalle'),
    path('dashboard/api/productos/<int:producto_id>/lotes/', views.api_lotes, name='api_lotes'),
    path('dashboard/api/productos/<int:producto_id>/lotes/<int:lote_id>/', views.api_lote_detalle, name='api_lote_detalle'),
    path('dashboard/api/pedidos/', views.api_pedidos, name='api_pedidos'),
    path('dashboard/api/pedidos/<int:pedido_id>/estado/', views.api_pedido_estado, name='api_pedido_estado'),
    path('dashboard/api/ventas/', views.api_ventas, name='api_ventas'),
    path('dashboard/api/ventas/<int:venta_id>/completar-pago/', views.api_venta_completar_pago, name='api_venta_completar_pago'),
    path('dashboard/api/ventas/<int:venta_id>/cancelar/', views.api_venta_cancelar, name='api_venta_cancelar'),
    path('dashboard/api/gastos/', views.api_gastos, name='api_gastos'),
    path('dashboard/api/gastos/<int:gasto_id>/', views.api_gasto_detalle, name='api_gasto_detalle'),
    path('dashboard/api/usuarios/', views.api_usuarios, name='api_usuarios'),
    path('dashboard/api/usuarios/<int:usuario_id>/', views.api_usuario_detalle, name='api_usuario_detalle'),
    path('dashboard/api/usuarios/<int:usuario_id>/toggle/', views.api_usuario_toggle, name='api_usuario_toggle'),
    path('dashboard/api/usuarios/<int:usuario_id>/reset-password/', views.api_usuario_reset_password, name='api_usuario_reset_password'),
    path('dashboard/api/pedidos/<int:pedido_id>/detalle/', views.api_pedido_detalle_admin, name='api_pedido_detalle_admin'),
    path('dashboard/api/pedidos/<int:pedido_id>/listo/', views.api_pedido_marcar_listo, name='api_pedido_marcar_listo'),
    path('dashboard/api/pedidos/<int:pedido_id>/completar-qr/', views.api_pedido_completar_qr, name='api_pedido_completar_qr'),
    path('dashboard/api/notificaciones/', views.api_notificaciones, name='api_notificaciones'),
    path('dashboard/api/notificaciones/contador/', views.api_notificaciones_contador, name='api_notificaciones_contador'),
    path('dashboard/api/notificaciones/<int:notif_id>/leer/', views.api_notificaciones_leer, name='api_notificaciones_leer'),
    path('dashboard/api/notificaciones/leer-todas/', views.api_notificaciones_leer_todas, name='api_notificaciones_leer_todas'),
    path('dashboard/api/qr-scan/', views.api_qr_scan, name='api_qr_scan'),
    path('validar-boleta/<slug:boleta_code>/', views.validar_boleta_view, name='validar_boleta'),
]

urlpatterns += api_urlpatterns
