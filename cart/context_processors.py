from .models import Cart


def cart_context(request):
    """Контекстний процесор для кошика - доступний на всіх сторінках"""
    cart = None
    cart_count = 0
    cart_total = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.total_items()
            cart_total = cart.total_price()
        except Cart.DoesNotExist:
            pass
    elif request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            cart_count = cart.total_items()
            cart_total = cart.total_price()
        except Cart.DoesNotExist:
            pass

    return {
        "cart": cart,
        "cart_count": cart_count,
        "cart_total": cart_total,
    }
