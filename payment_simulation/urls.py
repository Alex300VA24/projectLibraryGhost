from django.urls import path
from . import views

app_name = 'payment_simulation'

urlpatterns = [
    path('', views.simulation_home, name='home'),
    path('yape/', views.yape_entry, name='yape_entry'),
    path('yape/', views.yape_entry, name='yape'),
    path('yape/<int:order_id>/', views.yape_home, name='yape_with_order'),
    path('yape/<int:order_id>/qr/', views.yape_qr, name='yape_qr'),
    path('yape/<int:order_id>/code/', views.yape_code, name='yape_code'),
    path('yape/pedidos/', views.yape_pedidos, name='yape_pedidos'),
    path('plin/', views.plin_entry, name='plin_entry'),
    path('plin/', views.plin_entry, name='plin'),
    path('plin/<int:order_id>/', views.plin_home, name='plin_with_order'),
    path('plin/<int:order_id>/qr/', views.plin_qr, name='plin_qr'),
    path('plin/pedidos/', views.plin_pedidos, name='plin_pedidos'),
    path('transferencia/bcp/', views.bcp_transfer_simulation, name='bcp_transfer'),
    path('transferencia/bcp/<int:order_id>/', views.bcp_transfer_simulation, name='bcp_transfer_with_order'),
    path('transferencia/interbank/', views.interbank_transfer_simulation, name='interbank_transfer'),
    path('transferencia/interbank/<int:order_id>/', views.interbank_transfer_simulation, name='interbank_transfer_with_order'),
    path('check-order/<int:order_id>/', views.check_order_status, name='check_order'),
    path('validate-yape-code/<int:order_id>/<str:code>/', views.validate_yape_code, name='validate_yape_code'),
    path('validate-plin-code/<int:order_id>/<str:code>/', views.validate_plin_code, name='validate_plin_code'),
]
