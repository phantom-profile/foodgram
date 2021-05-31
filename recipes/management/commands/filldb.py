from random import randint, sample

from django.core.management.base import BaseCommand

from recipes.factories import RecipeFactory
from recipes.models import Favourite, Recipe, User

USERS = 100
MAX_RECIPES = 10
MAX_FAVORITES = 20


class Command(BaseCommand):
    """Custom `filldb` command.

    Django commands docs:
    https://docs.djangoproject.com/en/3.1/howto/custom-management-commands/

    """
    help = 'Fill DB with sample data'

    def handle(self, *args, **options):
        users = User.objects.all()

        for user in users:
            for _ in range(randint(0, MAX_RECIPES)):
                RecipeFactory(author=user)

        for user in User.objects.all():
            # User cannot favorite his own recipes
            recipes = list(Recipe.objects.exclude(author=user))
            to_favorite = sample(recipes, k=randint(1, MAX_FAVORITES))
            Favourite.objects.bulk_create([
                Favourite(user=user, recipe=recipe) for recipe in to_favorite
            ])
