from django.conf import settings
from django.db import models

from apps.products.models import Product


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pendiente'
    READY = 'ready', 'Listo para entrega'
    COMPLETED = 'completed', 'Completado'
    CANCELLED = 'cancelled', 'Cancelado'


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=64, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        owner = self.user.username if self.user else f'sesión {self.session_key}'
        return f'Carrito de {owner} — {self.items.count()} ítem(s)'


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Ítem del carrito'
        verbose_name_plural = 'Ítems del carrito'
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('yape', 'Yape'),
        ('plin', 'Plin'),
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('transferencia_bcp', 'Transferencia BCP'),
        ('transferencia_interbank', 'Transferencia Interbank'),
    ]

    YAPE_TYPE_CHOICES = [
        ('qr', 'QR'),
        ('code', 'Código de aprobación'),
    ]

    BANK_CHOICES = [
        ('bcp', 'BCP'),
        ('interbank', 'Interbank'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_CHOICES, blank=True, default=''
    )
    yape_type = models.CharField(
        max_length=10, choices=YAPE_TYPE_CHOICES, blank=True, default=''
    )
    yape_code = models.CharField(max_length=6, blank=True, default='')
    generated_yape_code = models.CharField(max_length=6, blank=True, default='')
    transfer_bank = models.CharField(
        max_length=20, choices=BANK_CHOICES, blank=True, default=''
    )
    boleta_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    order_number = models.CharField(max_length=6, unique=True, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    ready_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_marked_ready',
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_completed',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_created',
    )
    customer_name = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        num = self.order_number if self.order_number else f'{self.pk:05d}'
        return f'Pedido N°{num} — {self.user.username} ({self.get_status_display()})'

    @property
    def display_number(self):
        return self.order_number if self.order_number else f'{self.pk:05d}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name='order_items'
    )
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Ítem del pedido'
        verbose_name_plural = 'Ítems del pedido'

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notif para {self.user.username}: {self.title}'


class OrderHistory(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='history'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=200)
    from_status = models.CharField(max_length=20, blank=True, default='')
    to_status = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historial de pedido'
        verbose_name_plural = 'Historial de pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order} — {self.action} por {self.user}'
