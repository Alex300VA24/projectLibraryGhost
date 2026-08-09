import logging

from django.db import transaction
from django.http import HttpRequest

from ..models import Cart, CartItem
from ..selectors.cart_selector import get_or_create_cart
from ..validators.cart_validator import validate_stock_available

logger = logging.getLogger(__name__)


class CartService:

    @staticmethod
    def get_cart(request: HttpRequest) -> Cart:
        """Get or create a cart for the current request."""
        return get_or_create_cart(request)

    @staticmethod
    def get_cart_data(request: HttpRequest) -> dict:
        """Get cart data as a dictionary with items, total, and count."""
        from ..serializers import serialize_cart_data

        cart = get_or_create_cart(request)
        return serialize_cart_data(cart)

    @staticmethod
    def add_item(request: HttpRequest, product_id: int, quantity: int = 1):
        """
        Add a product to the cart.

        Raises:
            ValueError: If product has no stock.
        """
        from apps.products.models import Product

        product = Product.objects.get(pk=product_id, is_available=True)
        validate_stock_available(product, quantity)
        cart = get_or_create_cart(request)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity, "price": product.price},
        )
        if not created:
            item.quantity += quantity
            item.save()

        return item

    @staticmethod
    def update_item(request: HttpRequest, item_id: int, quantity: int):
        """Update cart item quantity. Deletes item if quantity <= 0."""
        cart = get_or_create_cart(request)
        item = CartItem.objects.get(pk=item_id, cart=cart)
        if quantity <= 0:
            item.delete()
            return None
        item.quantity = quantity
        item.save()
        return item

    @staticmethod
    def remove_item(request: HttpRequest, item_id: int) -> None:
        """Remove an item from the cart."""
        cart = get_or_create_cart(request)
        item = CartItem.objects.get(pk=item_id, cart=cart)
        item.delete()

    @staticmethod
    def clear_cart(request: HttpRequest) -> None:
        """Remove all items from the cart."""
        cart = get_or_create_cart(request)
        cart.items.all().delete()

    @staticmethod
    def merge_carts(session_key: str, user) -> None:
        """
        Merge an anonymous session cart into a user cart on login.
        Items from the anonymous cart are transferred to the user cart.
        """
        if not session_key:
            return
        anon_carts = Cart.objects.filter(session_key=session_key, user__isnull=True)
        if not anon_carts.exists():
            return
        user_cart, _ = Cart.objects.get_or_create(user=user)
        for anon_cart in anon_carts:
            for anon_item in anon_cart.items.select_related("product"):
                item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=anon_item.product,
                    defaults={"quantity": anon_item.quantity, "price": anon_item.product.price},
                )
                if not created:
                    item.quantity += anon_item.quantity
                    item.save()
            anon_cart.delete()

    @staticmethod
    def merge_anonymous_cart(request: HttpRequest, old_session_key: str = None) -> None:
        """
        Merge anonymous cart into user cart after login.

        Called from signals on user login.
        If the anonymous cart is empty, it is deleted without affecting the user cart.
        """
        sk = old_session_key or request.session.session_key
        if not sk:
            return
        anon_carts = Cart.objects.filter(session_key=sk, user__isnull=True)
        if not anon_carts.exists():
            return

        anon_items_exist = any(c.items.exists() for c in anon_carts)
        if not anon_items_exist:
            anon_carts.delete()
            return

        user_cart = Cart.objects.filter(user=request.user).first()
        if not user_cart:
            user_cart = Cart.objects.create(user=request.user)

        user_cart.items.all().delete()
        for anon_cart in anon_carts:
            for anon_item in anon_cart.items.select_related("product"):
                try:
                    CartItem.objects.create(
                        cart=user_cart,
                        product=anon_item.product,
                        quantity=anon_item.quantity,
                        price=anon_item.product.price,
                    )
                except Exception as e:
                    logger.warning("Error al fusionar item del carrito: %s — %s", anon_item.product, e)
            anon_cart.delete()
