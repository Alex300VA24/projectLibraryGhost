from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('api/datos/', views.catalog_api_data, name='catalog_api_data'),
    path('<slug:slug>/', views.product_detail_view, name='product_detail'),
]

# API endpoints para escáner de códigos de barras (POS / Flutter)
api_urlpatterns = [
    path('api/scanner/', views.scanner_barcode, name='scanner_barcode'),
    path('api/products/<str:barcode>/', views.product_by_barcode, name='product_by_barcode'),
    # path('api/scan-queue/', views.scan_queue_add, name='scan_queue_add'),
    # path('api/scan-queue/pending/', views.scan_queue_pending, name='scan_queue_pending'),
    # path('api/scan-queue/consume/', views.scan_queue_consume, name='scan_queue_consume'),
]
