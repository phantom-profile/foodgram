from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists, OuterRef

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=20, null=True)
    slug = models.SlugField(max_length=20)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(max_length=60)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name}, {self.unit}'


class RecipeQuerySet(models.QuerySet):
    def with_is_favourite(self, user_id: Optional[int]):
        """Annotate with favorite flag."""
        return self.annotate(is_favourite=Exists(
            Favourite.objects.filter(
                user_id=user_id,
                recipe_id=OuterRef('pk'),
            ),
        ))


class Recipe(models.Model):
    name = models.CharField(max_length=60)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    cook_time = models.PositiveIntegerField()
    description = models.TextField()
    pub_date = models.DateTimeField("date published",
                                    auto_now_add=True)
    image = models.ImageField(upload_to='recipe_pictures/',
                              blank=True,
                              null=True,)
    tags = models.ManyToManyField(Tag,
                                  related_name='tagged_recipes',
                                  through='RecipeTag')
    ingredients = models.ManyToManyField(Ingredient,
                                         related_name='ingredients',
                                         through='RecipeIngredient')

    objects = RecipeQuerySet.as_manager()

    def __str__(self):
        return f'{self.name} recipe by {self.author}'

    class Meta:
        ordering = ["-pub_date", ]


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe')
    amount = models.PositiveIntegerField()


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name='tags')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='tagged_recipe')


class Follow(models.Model):

    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE)

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписываться на самого себя')

    def __str__(self):
        return f'{self.user} follower of {self.author}'


class Favourite(models.Model):
    user = models.ForeignKey(User,
                             related_name='users_favourite',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='favourite_by',
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite_user_recipe'
            )
        ]


class Cart(models.Model):
    owner = models.OneToOneField(User,
                                 on_delete=models.CASCADE,
                                 related_name='cart')
    recipes = models.ManyToManyField(Recipe,
                                     through='CartRecipe')


class CartRecipe(models.Model):
    cart = models.ForeignKey(Cart,
                             on_delete=models.CASCADE,
                             related_name='in_cart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='carts')
