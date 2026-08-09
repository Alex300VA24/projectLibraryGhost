import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.products.models import Product
from ..models import CartItem
from ..selectors.cart_selector import get_or_create_cart
from ..selectors.order_selector import get_unpaid_pending_orders
from ..serializers import serialize_cart_item, serialize_cart_data
from ..services.cart_service import CartService


def cart_api_data(request):
    """Return cart data as JSON."""
    cart = get_or_create_cart(request)
    return JsonResponse(serialize_cart_data(cart))


@login_required
@require_POST
def empty_cart(request):
    """Empty the current user's cart."""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return JsonResponse({"success": True})


@login_required
def pago_view(request):
    """Render the payment page with cart items."""
    for order in get_unpaid_pending_orders(request.user):
        order.delete()

    cart = get_or_create_cart(request)
    items = [serialize_cart_item(item) for item in cart.items.select_related("product")]
    return render(request, "orders/pago.html", {
        "cart_items_json": json.dumps(items),
        "cart_total": float(cart.total),
    })


@login_required
def cart_view(request):
    """Render the cart page."""
    cart = get_or_create_cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@require_POST
def add_to_cart(request):
    """Add a product to the cart via AJAX."""
    if (
        request.user.is_authenticated
        and request.user.profile.role in ("employee", "empleado")
    ):
        return JsonResponse(
            {"success": False, "error": "No tienes permiso para agregar productos al carrito."},
            status=403,
        )

    data = json.loads(request.body)
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    product = Product.objects.get(pk=product_id, is_available=True)
    cart = get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity, "price": product.price},
    )
    if not created:
        item.quantity += quantity
        item.save()

    return JsonResponse({
        "success": True,
        "cart_total": float(cart.total),
        "cart_count": cart.items.count(),
    })


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity via AJAX."""
    data = json.loads(request.body)
    quantity = int(data.get("quantity", 1))

    cart = get_or_create_cart(request)
    item = CartItem.objects.get(pk=item_id, cart=cart)
    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()

    cart = item.cart if quantity > 0 else cart
    return JsonResponse({
        "success": True,
        "subtotal": float(item.subtotal) if quantity > 0 else 0,
        "cart_total": float(cart.total),
        "cart_count": cart.items.count(),
    })


@require_POST
def remove_from_cart(request, item_id):
    """Remove an item from the cart via AJAX."""
    cart = get_or_create_cart(request)
    item = CartItem.objects.get(pk=item_id, cart=cart)
    cart = item.cart
    item.delete()

    return JsonResponse({
        "success": True,
        "cart_total": float(cart.total),
        "cart_count": cart.items.count(),
    })
