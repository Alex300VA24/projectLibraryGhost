import os
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage


def _attach_logo(email_msg):
    """Attach the logo as an inline CID image."""
    logo_path = Path(settings.BASE_DIR) / 'static' / 'src' / 'images' / 'logo_sin_fondo.png'
    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<logo>')
            img.add_header('Content-Disposition', 'inline', filename='logo.png')
            email_msg.attach(img)
        return True
    return False


def _build_email_context(extra_context=None):
    ip_destino = getattr(settings, 'IP_DESTINO', '')
    domain = f"{ip_destino}:8000" if ip_destino else getattr(settings, 'COMPANY_DOMAIN', 'localhost:8000')
    protocol = 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'
    context = {
        "protocol": protocol,
        "domain": domain,
    }
    if extra_context:
        context.update(extra_context)
    return context


def _send_html_email(subject, template_name, context, recipient_list):
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        msg.attach_alternative(html_content, "text/html")
        _attach_logo(msg)
        msg.send(fail_silently=True)
    except Exception:
        pass


def send_welcome_email(user):
    context = _build_email_context({
        "user": user,
        "company_name": settings.COMPANY_NAME,
        "company_email": settings.COMPANY_EMAIL,
    })
    _send_html_email(
        subject=f"¡Bienvenido a {settings.COMPANY_NAME}!",
        template_name="emails/welcome_email.html",
        context=context,
        recipient_list=[user.email],
    )


def send_order_ready_email(order):
    context = _build_email_context({
        "order": order,
        "user": order.user,
        "company_name": settings.COMPANY_NAME,
        "company_email": settings.COMPANY_EMAIL,
    })
    _send_html_email(
        subject=f"Tu pedido N°{order.order_number or str(order.pk).zfill(6)} está listo - {settings.COMPANY_NAME}",
        template_name="emails/order_ready.html",
        context=context,
        recipient_list=[order.user.email],
    )


def send_receipt_email(order):
    context = _build_email_context({
        "order": order,
        "user": order.user,
        "company_name": settings.COMPANY_NAME,
        "company_email": settings.COMPANY_EMAIL,
    })
    _send_html_email(
        subject=f"Boleta #{order.boleta_code} - {settings.COMPANY_NAME}",
        template_name="emails/receipt_email.html",
        context=context,
        recipient_list=[order.user.email],
    )


def send_order_delivered_email(order):
    context = _build_email_context({
        "order": order,
        "user": order.user,
        "company_name": settings.COMPANY_NAME,
        "company_email": settings.COMPANY_EMAIL,
    })
    _send_html_email(
        subject=f"Tu pedido N°{order.order_number or str(order.pk).zfill(6)} ha sido entregado - {settings.COMPANY_NAME}",
        template_name="emails/order_delivered.html",
        context=context,
        recipient_list=[order.user.email],
    )
