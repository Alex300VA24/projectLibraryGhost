from django.urls import path

from . import views

urlpatterns = [
    path("carrito/", views.cart_view, name="cart"),
    path("carrito/api/datos/", views.cart_api_data, name="cart_api_data"),
    path("carrito/agregar/", views.add_to_cart, name="add_to_cart"),
    path("carrito/actualizar/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("carrito/eliminar/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("carrito/vaciar/", views.empty_cart, name="empty_cart"),
    path("pago/", views.pago_view, name="pago"),
    path("finalizar/", views.checkout, name="checkout"),
    path("crear-orden/", views.create_order, name="create_order"),
    path("pedidos/", views.my_orders_view, name="my_orders"),
    path("pedidos/api/datos/", views.orders_api_data, name="orders_api_data"),
    path("pedidos/<int:order_id>/", views.order_detail_view, name="order_detail"),
    path("pedidos/<int:order_id>/api/datos/", views.order_detail_api_data, name="order_detail_api_data"),
    path("pedidos/<int:order_id>/cancelar/", views.cancel_order, name="cancel_order"),
    path("pedidos/<int:order_id>/cancelar-no-pagado/", views.cancel_unpaid_order, name="cancel_unpaid_order"),
    path("payment/<int:order_id>/", views.payment_order_view, name="payment_order"),
    path("payment/<int:order_id>/api/datos/", views.payment_order_api, name="payment_order_api"),
    path("boleta/<slug:boleta_code>/", views.boleta_view, name="boleta"),
    path("boleta/<slug:boleta_code>/pdf/", views.boleta_pdf_view, name="boleta_pdf"),
    path("boleta/<slug:boleta_code>/verificar/", views.verify_boleta, name="verify_boleta"),
]
