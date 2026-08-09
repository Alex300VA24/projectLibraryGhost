from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio de venta')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Precio de compra')
    codigo = models.CharField(max_length=13, unique=True, db_index=True, blank=True, null=True, verbose_name='Código de barras (EAN-13)')
    stock = models.PositiveIntegerField(default=0)
    umbral = models.PositiveIntegerField(default=10, verbose_name='Umbral de stock')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def total_stock(self):
        return sum(b.quantity for b in self.batches.all()) + self.stock

    def __str__(self):
        return self.name


class ScanQueue(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('consumed', 'Consumido'),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='scan_queue_items'
    )
    barcode = models.CharField(max_length=13)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Escaneo en cola'
        verbose_name_plural = 'Escaneos en cola'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.barcode} - {self.product.name} ({self.status})'


class ProductBatch(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='batches'
    )
    batch_code = models.CharField(max_length=50, unique=True, verbose_name='Código de lote')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio de compra')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Cantidad')
    is_locked = models.BooleanField(default=False, verbose_name='Bloqueado para edición después de venta')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='Fecha de vencimiento')
    supplier = models.CharField(max_length=200, blank=True, verbose_name='Proveedor')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.batch_code:
            last = ProductBatch.objects.filter(product_id=self.product_id).order_by('-id').first()
            if last and last.batch_code:
                parts = last.batch_code.rsplit('-', 1)
                if parts[0] == f'LOTE-{self.product.id}':
                    try:
                        next_num = int(parts[1]) + 1
                    except (ValueError, IndexError):
                        next_num = 1
                else:
                    next_num = 1
            else:
                next_num = 1
            self.batch_code = f'LOTE-{self.product.id}-{next_num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.batch_code} - {self.product.name}'
