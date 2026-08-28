from .models import Cart, CartItem


def cart_context(request):
    cart = None
    cart_items_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        if request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if cart:
        cart_items_count = cart.total_items
    return {
        'cart_items_count': cart_items_count,
        'cart': cart,
    }
