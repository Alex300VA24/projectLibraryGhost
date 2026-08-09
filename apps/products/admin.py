from django.contrib import admin

from .models import Category, Product, ScanQueue


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'codigo', 'category', 'price', 'stock', 'is_available', 'created_at']
    list_filter = ['category', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'codigo', 'description']


@admin.register(ScanQueue)
class ScanQueueAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'product', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['barcode', 'product__name']
