import logging

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Role, UserProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        role_name = 'admin' if instance.is_staff else 'client'
        role_defaults = {
            'admin': 'Administrador',
            'employee': 'Empleado',
            'client': 'Cliente',
        }
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={'display_name': role_defaults.get(role_name, role_name.capitalize())},
        )
        UserProfile.objects.create(user=instance, role=role)


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """Fusiona el carrito anónimo al carrito del usuario al iniciar sesión.
    Usa la session_key antigua guardada antes de que Django la rote.
    """
    try:
        from apps.orders.services.cart_service import CartService
        old_sk = getattr(request, '_pre_login_session_key', None)
        CartService.merge_anonymous_cart(request, old_session_key=old_sk)
    except Exception as e:
        logger.warning("Error al fusionar carrito anónimo para %s: %s", user.username, e)
