from ..models import Cart, CartItem


def validate_cart_not_empty(cart: Cart) -> None:
    """
    Validate that the cart has at least one item.

    Raises:
        ValueError: If the cart is empty.
    """
    if not cart.items.exists():
        raise ValueError("Tu carrito está vacío.")


def validate_item_quantity(quantity: int) -> None:
    """
    Validate that quantity is a positive integer.

    Raises:
        ValueError: If quantity is not positive.
    """
    if quantity < 1:
        raise ValueError("La cantidad debe ser mayor a 0.")


def validate_stock_available(product, requested_quantity: int) -> None:
    """
    Validate that a product has sufficient stock.

    Raises:
        ValueError: If stock is insufficient.
    """
    if product.stock <= 0:
        raise ValueError("Producto sin stock disponible.")
    if product.stock < requested_quantity:
        raise ValueError(
            f"Stock insuficiente. Disponible: {product.stock}, solicitado: {requested_quantity}"
        )
