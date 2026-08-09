import random
from typing import Optional

from django.db import IntegrityError, transaction
from django.http import HttpRequest
from django.utils import timezone

from apps.products.models import Product

from ..models import Order, OrderHistory, OrderItem, OrderStatus
from ..selectors.cart_selector import get_or_create_cart
from ..validators.cart_validator import validate_cart_not_empty
from ..validators.order_validator import (
    validate_cancellation_limit,
    validate_order_cancellable,
)
from .cart_service import CartService
from .payment_service import build_simulation_qr
from .qr_service import generate_qr_base64


def generate_boleta_code() -> str:
    """
    Generate a unique sequential boleta code (race-condition-safe).

    Uses a retry loop to handle the unlikely event of a collision.

    Returns:
        A boleta code string like 'B001-000001'.
    """
    prefix = "B001"
    attempts = 0
    while attempts < 10:
        last = (
            Order.objects.filter(boleta_code__startswith=prefix + "-")
            .order_by("boleta_code")
            .last()
        )
        if last and last.boleta_code:
            parts = last.boleta_code.split("-")
            last_num = int(parts[1])
            next_num = last_num + 1
        else:
            next_num = 1
        code = f"{prefix}-{next_num:06d}"
        if not Order.objects.filter(boleta_code=code).exists():
            return code
        attempts += 1
    raise RuntimeError("No se pudo generar un código de boleta único.")


def generate_order_number() -> str:
    """
    Generate a unique sequential order number (race-condition-safe).

    Only assigned when the order is paid.

    Returns:
        An order number string like '000001'.
    """
    attempts = 0
    while attempts < 10:
        last = Order.objects.filter(order_number__isnull=False).order_by('order_number').last()
        if last and last.order_number:
            next_num = int(last.order_number) + 1
        else:
            next_num = 1
        number = f"{next_num:06d}"
        if not Order.objects.filter(order_number=number).exists():
            return number
        attempts += 1
    raise RuntimeError("No se pudo generar un número de pedido único.")


class OrderService:

    @staticmethod
    def create_order_from_cart(
        request: HttpRequest,
        payment_method: str = "",
        transfer_bank: str = "",
        yape_type: str = "",
        notes: str = "",
    ) -> dict:
        """
        Create an order from the current user's cart.

        Returns a dict with the order result data for the JSON response.
        """
        cart = get_or_create_cart(request)
        validate_cart_not_empty(cart)

        generated_code = ""
        if payment_method == "yape" and yape_type == "code":
            generated_code = str(random.randint(100000, 999999))

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total=cart.total,
                notes=notes,
                payment_method=payment_method,
                transfer_bank=transfer_bank,
                yape_type=yape_type,
                generated_yape_code=generated_code,
                boleta_code=generate_boleta_code(),
                order_number=generate_order_number(),
            )

            from core.views import _reduce_stock_fifo

            for cart_item in cart.items.select_related("product"):
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )
                _reduce_stock_fifo(cart_item.product, cart_item.quantity)

        sim_url, sim_qr_b64 = build_simulation_qr(
            request, payment_method, order.id
        )

        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number or "",
            "boleta_code": order.boleta_code,
            "simulation_url": sim_url,
            "simulation_qr_b64": sim_qr_b64,
            "generated_yape_code": generated_code,
        }

    @staticmethod
    def checkout_from_cart(
        request: HttpRequest,
        payment_method: str = "",
        transfer_bank: str = "",
        yape_type: str = "",
        yape_code: str = "",
        notes: str = "",
    ) -> dict:
        """
        Legacy checkout: create an order from cart (backwards-compatible).

        Returns a dict with the order result data for the JSON response.
        """
        cart = get_or_create_cart(request)
        validate_cart_not_empty(cart)

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total=cart.total,
                notes=notes,
                payment_method=payment_method,
                yape_type=yape_type,
                yape_code=yape_code,
                transfer_bank=transfer_bank,
                boleta_code=generate_boleta_code(),
            )

            from core.views import _reduce_stock_fifo

            for cart_item in cart.items.select_related("product"):
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )
                _reduce_stock_fifo(cart_item.product, cart_item.quantity)

        payment_url, qr_b64 = build_simulation_qr(
            request, payment_method, order.id
        )

        return {
            "success": True,
            "order": {
                "id": order.pk,
                "boleta_code": order.boleta_code,
                "total": float(order.total),
                "status": order.status,
                "status_display": order.get_status_display(),
                "payment_method": order.get_payment_method_display(),
                "qr_base64": qr_b64,
            },
        }

    @staticmethod
    def cancel_order(
        request: HttpRequest, order: Order
    ) -> dict:
        """
        Cancel an order. Returns a dict with redirect_name and toast params.

        For unpaid pending orders, the order is deleted entirely.
        For paid orders, the status is set to 'cancelled'.
        """
        if not order.is_paid and order.status == OrderStatus.PENDING:
            order.delete()
            return {
                "redirect_name": "pago",
                "toast_type": "success",
                "toast_title": "Pedido cancelado",
                "toast_desc": "El pedido pendiente fue eliminado.",
            }

        validate_order_cancellable(order)

        can_cancel, remaining = validate_cancellation_limit(request.user)
        if not can_cancel:
            return {
                "redirect_name": "my_orders",
                "toast_type": "error",
                "toast_title": "Límite de cancelaciones alcanzado",
                "toast_desc": "Has alcanzado el límite de 3 cancelaciones este mes.",
            }

        old_status = order.status
        order.status = OrderStatus.CANCELLED
        order.save()
        OrderHistory.objects.create(
            order=order,
            user=request.user if request.user.is_authenticated else None,
            action="Cancelar pedido",
            from_status=old_status,
            to_status=OrderStatus.CANCELLED,
        )
        return {
            "redirect_name": "my_orders",
            "toast_type": "success",
            "toast_title": "Pedido cancelado",
            "toast_desc": f"Pedido N°{order.display_number} cancelado.",
        }

    @staticmethod
    def cancel_unpaid_order(request: HttpRequest, order: Order) -> dict:
        """Delete an unpaid pending order. Returns cart data."""
        order.delete()
        cart = get_or_create_cart(request)
        return {
            "success": True,
            "cart_total": float(cart.total),
            "cart_count": cart.items.count(),
        }

    @staticmethod
    def advance_order_status(order) -> dict:
        """
        Legacy advance method - maintains backward compatibility.
        """
        if order.status == OrderStatus.CANCELLED:
            return {"success": False, "error": "Este pedido fue cancelado."}

        if order.status == OrderStatus.COMPLETED:
            return {
                "success": True,
                "message": "Este pedido ya fue completado.",
                "status": order.status,
            }

        next_status = {
            OrderStatus.PENDING: OrderStatus.READY,
            OrderStatus.READY: OrderStatus.COMPLETED,
        }
        new_status = next_status.get(order.status, OrderStatus.COMPLETED)
        order.status = new_status
        order.save()

        return {
            "success": True,
            "message": f"Pedido N°{order.display_number} actualizado a {order.get_status_display()}.",
            "status": order.status,
            "status_display": order.get_status_display(),
            "is_paid": order.is_paid,
        }

    @staticmethod
    def mark_as_ready(order, user) -> dict:
        if order.status != OrderStatus.PENDING:
            return {"success": False, "error": "El pedido no está pendiente."}
        old_status = order.status
        order.status = OrderStatus.READY
        order.ready_at = timezone.now()
        order.ready_by = user
        order.save()
        OrderHistory.objects.create(
            order=order,
            user=user,
            action="Marcar como listo para entrega",
            from_status=old_status,
            to_status=OrderStatus.READY,
        )
        return {
            "success": True,
            "message": f"Pedido N°{order.display_number} marcado como listo para entrega.",
            "status": order.status,
            "status_display": order.get_status_display(),
        }

    @staticmethod
    def mark_as_completed(order, user) -> dict:
        if order.status != OrderStatus.READY:
            return {"success": False, "error": "El pedido no está listo para entrega."}
        old_status = order.status
        order.status = OrderStatus.COMPLETED
        order.completed_at = timezone.now()
        order.completed_by = user
        order.save()
        OrderHistory.objects.create(
            order=order,
            user=user,
            action="Completar pedido (QR)",
            from_status=old_status,
            to_status=OrderStatus.COMPLETED,
        )
        return {
            "success": True,
            "message": f"Pedido N°{order.display_number} completado.",
            "status": order.status,
            "status_display": order.get_status_display(),
            "validated_by": user.get_full_name() or user.username if user else None,
        }
