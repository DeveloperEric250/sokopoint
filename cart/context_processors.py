from .cart import Cart


def cart_context(request):
    """Make the cart available in every template."""
    return {'cart': Cart(request)}
