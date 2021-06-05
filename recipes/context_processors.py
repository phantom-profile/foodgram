from recipes.models import Cart


def purchases(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get_or_create(owner=request.user)[0]
        return {'get_purchases_count': cart.recipes.count()}
    return {'get_purchases_count': 0}
