from typing import Optional

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists, OuterRef

User = get_user_model()

min_validator = MinValueValidator(1, 'Значение должно быть больше 0')


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name='тэг')
    color = models.CharField(max_length=20, null=True, verbose_name='цвет')
    slug = models.SlugField(max_length=20, verbose_name='ссылка')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(max_length=60, verbose_name='ингридиент')
    unit = models.CharField(max_length=20, verbose_name='ед.')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

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
    name = models.CharField(max_length=60, verbose_name='рецепт')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='автор')
    cook_time = models.PositiveIntegerField(validators=[min_validator, ],
                                            verbose_name='время приготовления')
    description = models.TextField(verbose_name='описание')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата публикации')
    image = models.ImageField(upload_to='recipe_pictures/',
                              blank=True,
                              null=True,
                              verbose_name='картинка')
    tags = models.ManyToManyField(Tag,
                                  related_name='tagged_recipes',
                                  through='RecipeTag',
                                  verbose_name='тэги')
    ingredients = models.ManyToManyField(Ingredient,

                                         related_name='ingredients',
                                         through='RecipeIngredient',
                                         verbose_name='ингридиенты')

    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ["-pub_date", ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} recipe by {self.author}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient',
                                   verbose_name='ингридиент')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe',
                               verbose_name='рецепт')
    amount = models.PositiveIntegerField(validators=[min_validator, ],
                                         verbose_name='количество')


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name='tags',
                            verbose_name='тэг')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='tagged_recipe',
                               verbose_name='рецепт')


class Follow(models.Model):

    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE,
                             verbose_name='подписчик')
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE,
                               verbose_name='подписан на')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписываться на самого себя')

    def __str__(self):
        return f'{self.user} follower of {self.author}'


class Favourite(models.Model):
    user = models.ForeignKey(User,
                             related_name='users_favourite',
                             on_delete=models.CASCADE,
                             verbose_name='оценил')
    recipe = models.ForeignKey(Recipe,
                               related_name='favourite_by',
                               on_delete=models.CASCADE,
                               verbose_name='оцененный рецепт')

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
                                 related_name='cart',
                                 verbose_name='покупатель')
    recipes = models.ManyToManyField(Recipe,
                                     through='CartRecipe',
                                     verbose_name='рецепт в покупках')

    class Meta:
        verbose_name = 'Тележка покупок'
        verbose_name_plural = 'Тележки покупок'


class CartRecipe(models.Model):
    cart = models.ForeignKey(Cart,
                             on_delete=models.CASCADE,
                             related_name='in_cart',
                             verbose_name='тележка покупок')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='carts',
                               verbose_name='покупка')
