"""
Legacy re-exports for backward compatibility.

New code should import directly from the specific service module.
"""
from .cart_service import CartService

__all__ = ["CartService"]
