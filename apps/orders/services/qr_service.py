import base64
import io

import qrcode


def generate_qr_base64(url: str) -> str:
    """
    Generate a QR code image from a URL and return it as a base64-encoded string.

    Args:
        url: The URL to encode in the QR code.

    Returns:
        Base64-encoded PNG image string.
    """
    qr = qrcode.make(url, box_size=8, border=2)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()
