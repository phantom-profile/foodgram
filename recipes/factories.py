from random import choice

import factory
from factory import fuzzy

from users.factories import UserFactory

from . import models


class BaseRecipeFactory(factory.django.DjangoModelFactory):
    """Factory that generates Recipes without Ingredients."""
    author = factory.SubFactory(UserFactory)
    name = factory.Faker('word')
    image = factory.django.ImageField(width=1000)
    description = factory.Faker('text')
    # no ingredients
    cook_time = fuzzy.FuzzyInteger(10, 120)

    class Meta:
        model = models.Recipe


class RecipeTagFactory(factory.django.DjangoModelFactory):
    recipe = factory.SubFactory(BaseRecipeFactory)

    class Meta:
        model = models.RecipeTag

    @factory.lazy_attribute
    def tag(self):
        return models.Tag.objects.first()


class RecipeIngredientFactory(factory.django.DjangoModelFactory):
    """Factory that generates Recipes with Ingredients."""
    recipe = factory.SubFactory(BaseRecipeFactory)
    amount = fuzzy.FuzzyInteger(50, 500)

    class Meta:
        model = models.RecipeIngredient

    @factory.lazy_attribute
    def ingredient(self):
        return choice(models.Ingredient.objects.all())


class RecipeFactory(BaseRecipeFactory):
    """Factory that generates Recipes with 5 Ingredients."""

    tag_1 = factory.RelatedFactory(
        RecipeTagFactory,
        factory_related_name='recipe'
    )

    ingredient_1 = factory.RelatedFactory(
        RecipeIngredientFactory,
        factory_related_name='recipe',
    )
    ingredient_2 = factory.RelatedFactory(
        RecipeIngredientFactory,
        factory_related_name='recipe',
    )
    ingredient_3 = factory.RelatedFactory(
        RecipeIngredientFactory,
        factory_related_name='recipe',
    )
    ingredient_4 = factory.RelatedFactory(
        RecipeIngredientFactory,
        factory_related_name='recipe',
    )
    ingredient_5 = factory.RelatedFactory(
        RecipeIngredientFactory,
        factory_related_name='recipe',
    )
