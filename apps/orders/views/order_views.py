from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from ..models import Order
from ..selectors.order_selector import get_user_orders
from ..serializers import serialize_order_with_count, serialize_order_items
from ..services.qr_service import generate_qr_base64
from ..services.receipt_service import build_boleta_qr
from ..validators.order_validator import validate_cancellation_limit


@login_required
def my_orders_view(request):
    """Render the user's order history page."""
    orders = get_user_orders(request).order_by('created_at')
    _, remaining = validate_cancellation_limit(request.user)
    return render(request, "orders/my_orders.html", {
        "orders": orders,
        "remaining_cancellations": remaining,
    })


@login_required
def orders_api_data(request):
    """Return user orders as JSON."""
    orders = get_user_orders(request).order_by("-created_at")
    data = [serialize_order_with_count(o) for o in orders]
    return JsonResponse({"success": True, "orders": data})


@login_required
def order_detail_api_data(request, order_id):
    """Return single order detail as JSON."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    qr_b64 = None
    if order.boleta_code:
        qr_b64 = build_boleta_qr(request, order)

    data = serialize_order_with_count(order)
    data["items"] = serialize_order_items(order.items.all())
    data["qr_base64"] = qr_b64
    return JsonResponse({"success": True, "order": data})


@login_required
def order_detail_view(request, order_id):
    """Render single order detail page."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
