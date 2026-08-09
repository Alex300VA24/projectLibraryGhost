import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..services.order_service import OrderService


@login_required
@require_POST
def create_order(request):
    """Create an order from the current cart with payment details."""
    data = json.loads(request.body) if request.body else {}
    result = OrderService.create_order_from_cart(
        request,
        payment_method=data.get("payment_method", ""),
        transfer_bank=data.get("transfer_bank", ""),
        yape_type=data.get("yape_type", ""),
        notes=data.get("notes", ""),
    )
    return JsonResponse(result)


@login_required
@require_POST
def checkout(request):
    """Legacy checkout (backwards-compatible)."""
    data = json.loads(request.body) if request.body else {}
    result = OrderService.checkout_from_cart(
        request,
        payment_method=data.get("payment_method", ""),
        transfer_bank=data.get("transfer_bank", ""),
        yape_type=data.get("yape_type", ""),
        yape_code=data.get("yape_code", ""),
        notes=data.get("notes", ""),
    )
    return JsonResponse(result)
