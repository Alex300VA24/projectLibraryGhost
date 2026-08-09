from rest_framework import serializers
from .models import Product, ScanQueue


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'barcode', 'name', 'price', 'stock', 'description']

    barcode = serializers.CharField(source='codigo')


class ScanQueueSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ScanQueue
        fields = ['id', 'product', 'barcode', 'status', 'created_at']
