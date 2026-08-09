from typing import Optional

from django.http import HttpRequest

from ..models import Cart


def get_or_create_cart(request: HttpRequest) -> Cart:
    """
    Get or create a cart for the current user or session.

    Authenticated users get a user-linked cart.
    Anonymous users get a session-key-linked cart.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def get_anonymous_carts(session_key: str) -> list[Cart]:
    """Get all anonymous carts for a given session key."""
    return list(Cart.objects.filter(session_key=session_key, user__isnull=True))
