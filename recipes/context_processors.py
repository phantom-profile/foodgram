from recipes.models import Cart


def purchases(request):
    cart = Cart.objects.get_or_create(owner=request.user)[0]
    return {'get_purchases_count': cart.recipes.count()}
