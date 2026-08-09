from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from ..models import Order
from ..serializers import serialize_order_items, serialize_payment_order
from ..services.order_service import OrderService
from ..services.payment_service import build_simulation_qr, build_simulation_url
from ..services.qr_service import generate_qr_base64


@login_required
def payment_order_view(request, order_id):
    """Render the payment page for a specific order."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.is_paid:
        return redirect("boleta", boleta_code=order.boleta_code)

    sim_url = build_simulation_url(order.payment_method, order.id)
    items = serialize_order_items(order.items.all())

    return render(request, "orders/payment_order.html", {
        "order": order,
        "items": items,
        "simulation_url": sim_url,
    })


@login_required
def payment_order_api(request, order_id):
    """Return payment order data as JSON."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    qr_b64 = ""
    if order.boleta_code:
        payment_url = request.build_absolute_uri(
            reverse("payment_order", kwargs={"order_id": order.id})
        )
        qr_b64 = generate_qr_base64(payment_url)

    sim_url, sim_qr_b64 = build_simulation_qr(
        request, order.payment_method, order.id
    )

    data = serialize_payment_order(order, qr_b64, sim_qr_b64)
    return JsonResponse({"success": True, "order": data})


@login_required
@require_POST
def cancel_order(request, order_id):
    """Cancel a pending or confirmed order (redirect-based)."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    result = OrderService.cancel_order(request, order)
    url = reverse(result["redirect_name"])
    qs = (
        f'toast_type={quote(result["toast_type"])}'
        f'&toast_title={quote(result["toast_title"])}'
        f'&toast_desc={quote(result["toast_desc"])}'
    )
    return redirect(f'{url}?{qs}')


@login_required
@require_POST
def cancel_unpaid_order(request, order_id):
    """Delete an unpaid pending order via AJAX."""
    order = get_object_or_404(Order, pk=order_id, user=request.user, is_paid=False, status="pending")
    result = OrderService.cancel_unpaid_order(request, order)
    return JsonResponse(result)
