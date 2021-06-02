import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, get_object_or_404

from recipes.models import Ingredient, RecipeIngredient


@login_required
def download_purchases(request):
    recipes = request.user.cart.recipes.all()
    ingredient_qs = RecipeIngredient.objects.filter(
        recipe__in=recipes
    )

    ingredient_list = {}
    for r_i in ingredient_qs.values():
        pk, ingredient_id, recipe_id, amount = r_i.values()
        ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
        full_name = ingredient.name + ', ' + ingredient.unit
        if full_name in ingredient_list:
            ingredient_list[full_name] += amount
        else:
            ingredient_list[full_name] = amount

    file_name = f'{settings.MEDIA_ROOT}/{request.user.username}_cart.txt'
    file = open(file_name, 'w', encoding='utf-8')

    for name, amount in ingredient_list.items():
        ingrid_line = f'{name} - {amount}\n'
        file.write(ingrid_line)
    file.close()
    file = open(file_name, 'r', encoding='utf-8')
    response = HttpResponse(file.read())
    file.close()

    response['Content-Type'] = 'text/plain'
    response['Content-Length'] = str(os.stat(file_name).st_size)
    short_name = f'{request.user.username}_cart.txt'
    response['Content-Disposition'] = f"attachment; filename={short_name}"
    os.remove(file_name)

    return response
