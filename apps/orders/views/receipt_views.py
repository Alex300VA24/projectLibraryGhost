from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from ..models import Order
from ..services.order_service import OrderService
from ..services.receipt_service import build_boleta_qr, generate_boleta_pdf


@login_required
def boleta_view(request, boleta_code):
    """Render the boleta (receipt) page for an order."""
    if request.user.is_staff:
        order = get_object_or_404(Order, boleta_code=boleta_code)
    else:
        order = get_object_or_404(Order, boleta_code=boleta_code, user=request.user)
    qr_b64 = build_boleta_qr(request, order)

    from payment_simulation.utils import build_simulation_absolute_uri
    payment_url = build_simulation_absolute_uri(
        request, "payment_order", order_id=order.id
    )

    return render(request, "orders/boleta.html", {
        "order": order,
        "qr_b64": qr_b64,
        "verify_url": payment_url,
    })


@login_required
def boleta_pdf_view(request, boleta_code):
    """Generate and download a PDF of the boleta."""
    if request.user.is_staff:
        order = get_object_or_404(Order, boleta_code=boleta_code)
    else:
        order = get_object_or_404(Order, boleta_code=boleta_code, user=request.user)
    qr_b64 = build_boleta_qr(request, order)

    from payment_simulation.utils import build_simulation_absolute_uri
    payment_url = build_simulation_absolute_uri(
        request, "payment_order", order_id=order.id
    )

    return generate_boleta_pdf(request, order, qr_b64, payment_url)


@login_required
@require_POST
def verify_boleta(request, boleta_code):
    """Staff-only endpoint to advance order status."""
    if not request.user.profile.role in ("admin", "employee"):
        return JsonResponse(
            {"success": False, "error": "Solo el personal autorizado puede verificar boletas."}
        )

    order = get_object_or_404(Order, boleta_code=boleta_code)
    result = OrderService.advance_order_status(order)
    return JsonResponse(result)
