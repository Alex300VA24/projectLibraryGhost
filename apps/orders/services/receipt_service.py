import io

from django.http import HttpResponse
from django.template.loader import render_to_string

from xhtml2pdf import pisa

from ..models import Order
from .qr_service import generate_qr_base64


def build_boleta_qr(request, order: Order) -> str:
    """Build a QR code for the boleta's validation URL."""
    from payment_simulation.utils import build_simulation_absolute_uri

    validation_url = build_simulation_absolute_uri(
        request, "validar_boleta", boleta_code=order.boleta_code
    )
    return generate_qr_base64(validation_url)


def generate_boleta_pdf(
    request, order: Order, qr_b64: str, verify_url: str
) -> HttpResponse:
    """
    Generate a PDF for a boleta (receipt).

    Returns:
        HttpResponse with PDF content on success, or error response on failure.
    """
    html_string = render_to_string(
        "orders/boleta_pdf.html",
        {
            "order": order,
            "qr_b64": qr_b64,
            "verify_url": verify_url,
        },
    )

    result = io.BytesIO()
    pdf = pisa.pisaDocument(
        io.BytesIO(html_string.encode("utf-8")), result, encoding="utf-8"
    )

    if pdf.err:
        return HttpResponse("Error al generar el PDF", status=500)

    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="boleta_{order.boleta_code}.pdf"'
    )
    return response
