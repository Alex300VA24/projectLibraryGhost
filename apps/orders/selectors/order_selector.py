from typing import Optional

from django.http import HttpRequest

from ..models import Order


def get_user_orders(request: HttpRequest):
    """Return active (non-pending-unpaid) orders for the current user."""
    return Order.objects.filter(user=request.user).exclude(
        status="pending", is_paid=False
    )


def get_user_order_by_id(order_id: int, request: HttpRequest) -> Order:
    """Get a single order belonging to the current user by ID."""
    return Order.objects.get(pk=order_id, user=request.user)


def get_order_by_boleta_code(boleta_code: str, request: HttpRequest) -> Order:
    """Get an order by boleta code for the current user."""
    return Order.objects.get(boleta_code=boleta_code, user=request.user)


def get_unpaid_pending_orders(user) -> list[Order]:
    """Get all unpaid pending orders for a user."""
    return list(
        Order.objects.filter(user=user, is_paid=False, status="pending")
    )
