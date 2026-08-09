from django.utils import timezone

from ..models import Order, OrderHistory, OrderStatus


def validate_order_cancellable(order: Order) -> None:
    """
    Validate that an order can be cancelled.

    An order can be cancelled if it is:
    - unpaid and pending (can be deleted entirely), or
    - in 'pending' or 'confirmed' status (can be set to cancelled).

    Raises:
        ValueError: If the order cannot be cancelled.
    """
    if order.status != "pending":
        raise ValueError("No se puede cancelar un pedido que no esté pendiente.")


MAX_CANCELLATIONS_PER_MONTH = 3


def validate_cancellation_limit(user) -> tuple[bool, int]:
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    cancelled_count = OrderHistory.objects.filter(
        user=user,
        to_status=OrderStatus.CANCELLED,
        created_at__gte=month_start,
    ).count()

    remaining = max(0, MAX_CANCELLATIONS_PER_MONTH - cancelled_count)
    return remaining > 0, remaining


def validate_staff_role(user) -> None:
    """
    Validate that the user has staff/admin/employee role.

    Raises:
        ValueError: If the user lacks permissions.
    """
    if not user.profile.role in ("admin", "employee"):
        raise ValueError("Solo el personal autorizado puede realizar esta acción.")
