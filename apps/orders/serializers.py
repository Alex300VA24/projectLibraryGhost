from typing import Any, Dict, List, Optional

from .models import Cart, CartItem, Order, OrderItem


def serialize_cart_item(item: CartItem) -> Dict[str, Any]:
    """Serialize a single cart item to a dict."""
    return {
        "id": item.id,
        "product_id": item.product_id,
        "name": item.product.name,
        "price": float(item.price),
        "quantity": item.quantity,
        "subtotal": float(item.subtotal),
        "image": item.product.image.url if item.product.image else None,
    }


def serialize_order_basic(order: Order) -> Dict[str, Any]:
    """Serialize an order with basic fields (no items)."""
    return {
        "id": order.pk,
        "order_number": order.order_number or "",
        "status": order.status,
        "status_display": order.get_status_display(),
        "total": float(order.total),
        "date": order.created_at.strftime("%d/%m/%Y %H:i"),
        "notes": order.notes or "",
        "boleta_code": order.boleta_code or "",
        "payment_method": order.get_payment_method_display() if order.payment_method else "",
        "is_paid": order.is_paid,
    }


def serialize_order_with_count(order: Order) -> Dict[str, Any]:
    """Serialize an order with items count."""
    data = serialize_order_basic(order)
    data["items_count"] = order.items.count()
    return data


def serialize_order_item(item: OrderItem) -> Dict[str, Any]:
    """Serialize a single order item to a dict."""
    return {
        "name": item.product_name,
        "quantity": item.quantity,
        "price": float(item.price),
        "subtotal": float(item.subtotal),
        "image": item.product.image.url if item.product and item.product.image else None,
    }


def serialize_order_items(items) -> List[Dict[str, Any]]:
    """Serialize a queryset of order items."""
    return [serialize_order_item(item) for item in items]


def serialize_cart_items(cart: Cart) -> List[Dict[str, Any]]:
    """Serialize all items in a cart."""
    return [serialize_cart_item(item) for item in cart.items.select_related("product")]


def serialize_cart_data(cart: Cart) -> Dict[str, Any]:
    """Serialize cart with items, total, and count."""
    items = serialize_cart_items(cart)
    return {
        "success": True,
        "items": items,
        "total": float(cart.total),
        "count": len(items),
    }


def serialize_payment_order(order: Order, qr_base64: str = "", sim_qr_b64: str = "") -> Dict[str, Any]:
    """Serialize order with payment details."""
    return {
        "id": order.pk,
        "order_number": order.order_number or "",
        "status": order.status,
        "status_display": order.get_status_display(),
        "total": float(order.total),
        "date": order.created_at.strftime("%d/%m/%Y %H:%M"),
        "items": serialize_order_items(order.items.all()),
        "boleta_code": order.boleta_code or "",
        "payment_method": order.payment_method,
        "payment_method_display": order.get_payment_method_display(),
        "yape_type": order.yape_type,
        "transfer_bank": order.transfer_bank,
        "is_paid": order.is_paid,
        "qr_base64": qr_base64,
        "simulation_qr_b64": sim_qr_b64,
        "generated_yape_code": order.generated_yape_code,
    }
