from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.api.serializers import IngredientSerializer
from recipes.models import (Cart, CartRecipe, Favourite, Follow, Ingredient,
                            User)


class AddToFavorites(APIView):
    """Add a Recipe to Favorites of a User."""

    def post(self, request, format=None):
        Favourite.objects.get_or_create(
            user=request.user,
            recipe_id=request.data['id'],
        )

        return Response({'success': True}, status=status.HTTP_200_OK)


class RemoveFromFavorites(APIView):
    """Remove a Recipe from User's Favorites."""

    def delete(self, request, pk, format=None):
        Favourite.objects.filter(recipe_id=pk, user=request.user).delete()
        return Response({'success': True}, status=status.HTTP_200_OK)


class Subscribe(APIView):

    def post(self, request, format=None):
        Follow.objects.get_or_create(
            user=request.user,
            author_id=request.data['id']
        )
        return Response({'success': True}, status=status.HTTP_200_OK)


class UnSubscribe(APIView):

    def delete(self, request, pk, format=None):
        author = User.objects.get(pk=pk)
        Follow.objects.filter(user=request.user, author=author).delete()
        return Response({'success': True}, status=status.HTTP_200_OK)


class GetIngredients(APIView):
    def get(self, request):
        queryset = Ingredient.objects.all()
        user_input = request.query_params.get('query').strip('/')
        if user_input is not None:
            queryset = queryset.filter(name__startswith=user_input)
        list_ingredients = []
        for ingredient in queryset:
            list_ingredients.append(IngredientSerializer(ingredient).data)
        return Response(list_ingredients)


class AddPurchase(APIView):
    def post(self, request, format=None):
        cart = Cart.objects.get_or_create(
            owner=request.user
        )
        CartRecipe.objects.get_or_create(
            cart_id=cart[0].id,
            recipe_id=request.data['id'],
        )

        return Response({'success': True}, status=status.HTTP_200_OK)


class RemoveFromPurchases(APIView):
    def delete(self, request, pk, format=None):
        cart = Cart.objects.get_or_create(
            owner=request.user
        )
        CartRecipe.objects.filter(recipe_id=pk, cart_id=cart[0].pk).delete()
        return Response({'success': True}, status=status.HTTP_200_OK)
