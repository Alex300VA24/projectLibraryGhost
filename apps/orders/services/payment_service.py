from typing import Dict, Optional, Tuple

from django.http import HttpRequest
from django.urls import reverse

from ..models import Order
from .qr_service import generate_qr_base64


PAYMENT_VIEW_NAME_MAP: Dict[str, str] = {
    "yape": "payment_simulation:yape_with_order",
    "plin": "payment_simulation:plin_with_order",
    "transferencia_bcp": "payment_simulation:bcp_transfer_with_order",
    "transferencia_interbank": "payment_simulation:interbank_transfer_with_order",
}


def get_simulation_view_name(payment_method: str) -> str:
    """Get the simulation view name for a given payment method."""
    return PAYMENT_VIEW_NAME_MAP.get(payment_method, "payment_simulation:home")


def build_simulation_url(payment_method: str, order_id: int) -> str:
    """Build the simulation URL (relative) for a payment method and order."""
    view_name = get_simulation_view_name(payment_method)
    if payment_method in ("yape", "plin", "transferencia_bcp", "transferencia_interbank"):
        return reverse(view_name, kwargs={"order_id": order_id})
    return reverse("payment_simulation:home")


def build_simulation_qr(
    request: HttpRequest, payment_method: str, order_id: int
) -> Tuple[str, str]:
    """
    Build the simulation URL and its QR code for a payment method.

    Returns:
        Tuple of (simulation_url, simulation_qr_base64).
    """
    from payment_simulation.utils import build_simulation_absolute_uri

    view_name = get_simulation_view_name(payment_method)
    kwargs_map = (
        {"order_id": order_id}
        if payment_method in ("yape", "plin", "transferencia_bcp", "transferencia_interbank")
        else {}
    )
    sim_absolute_url = build_simulation_absolute_uri(
        request, view_name, **kwargs_map,
    )
    sim_qr_b64 = generate_qr_base64(sim_absolute_url)
    sim_url = build_simulation_url(payment_method, order_id)
    return sim_url, sim_qr_b64
