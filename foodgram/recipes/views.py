import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.views import generic
from django.views.generic import DetailView, ListView

from recipes.forms import RecipeForm
from recipes.models import Cart, Ingredient, Recipe, RecipeIngredient, User


class IsFavouriteMixin:
    """Add annotation with favorite mark to the View."""

    def get_queryset(self):
        """Annotate with favorite mark."""
        qs = super().get_queryset()
        qs = (
            qs
            .select_related('author')
            .with_is_favourite(user_id=self.request.user.id)
        )

        return qs


class CartMixin(generic.base.ContextMixin):
    page_title = ''
    active_menu = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['cart'] = get_object_or_404(Cart, owner=self.request.user)
        return context


class BaseRecipeListView(ListView, IsFavouriteMixin, CartMixin):
    """Base view for Recipe list."""
    context_object_name = 'recipe_list'
    queryset = Recipe.objects.all()
    paginate_by = 6
    page_title = None

    def get_queryset(self):
        """Annotate with favorite mark."""
        qs = super().get_queryset()
        qs = (
            qs
            .prefetch_related('recipe__ingredient')
            .with_is_favourite(user_id=self.request.user.id)
        )
        tags = self.request.GET.getlist('tags')
        for tag in tags:
            qs = qs.filter(tags__slug__exact=tag)

        return qs


class IndexView(BaseRecipeListView):
    """Main page that displays list of Recipes."""
    template_name = 'recipes/recipe_list.html'


class FavouriteView(LoginRequiredMixin, BaseRecipeListView):
    """List of current user's favorite Recipes."""
    template_name = 'recipes/recipe_list.html'

    def get_queryset(self):
        """Display favourite recipes only."""
        qs = super().get_queryset()
        qs = qs.filter(favourite_by__user=self.request.user)
        print(self.request.GET)
        return qs


class ProfileView(BaseRecipeListView, CartMixin):
    """User's page with its name and list of authored Recipes."""
    template_name = 'recipes/profile_recipe_list.html'

    def get(self, request, *args, **kwargs):
        """Store `user` parameter for data filtration purposes."""
        self.user = get_object_or_404(User, username=kwargs.get('username'))

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Display owner recipes only."""
        qs = super().get_queryset()
        qs = qs.filter(author=self.user)

        return qs

    def _get_page_title(self):
        """Get page title."""
        return self.user.get_full_name()

    def get_context_data(self, **kwargs):
        owner = self.user
        viewer = self.request.user
        if viewer.is_authenticated:
            following = viewer.follower.filter(author=owner)
        else:
            following = False

        kwargs.update({'user': viewer})
        kwargs.update({'owner': self.user})
        kwargs.update({'following': following})
        context = super().get_context_data(**kwargs)
        return context


class RecipeDetailView(DetailView, IsFavouriteMixin, CartMixin):
    """Page with Recipe details."""
    queryset = Recipe.objects.all()
    template_name = 'recipes/recipe_detail.html'

    def get_queryset(self):
        """Annotate with favorite mark."""
        qs = super().get_queryset()
        qs = (
            qs
                .prefetch_related('recipe__ingredient')
                .with_is_favourite(user_id=self.request.user.id)
        )

        return qs


class MyFollowingsView(ListView, CartMixin, LoginRequiredMixin):
    context_object_name = 'users'
    paginate_by = 3
    template_name = 'recipes/my_subscriptions.html'

    def get_queryset(self):
        qs = User.objects.filter(following__user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        following = True
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['following'] = following

        return context


class MyCartView(ListView, CartMixin, LoginRequiredMixin):
    context_object_name = 'recipes'
    paginate_by = 6
    template_name = 'recipes/purchase_list.html'

    def get_queryset(self):
        cart = Cart.objects.get_or_create(owner=self.request.user)[0]
        recipes = cart.recipes.all()
        return recipes


@login_required
def download_purchases(request):
    recipes = request.user.cart.recipes.all()
    ingredient_qs = (recipes
                     .values('ingredients__name',
                             'ingredients__unit',
                             'ingredients__ingredient__amount')
                     )

    ingredient_list = {}
    for ingredient in ingredient_qs:
        name, unit, amount = ingredient.values()
        full_name = name + ', ' + unit
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


def get_ingredients(request):
    ingredients = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            value_ingredient = key[15:]
            ingredients[request.POST[key]] = request.POST[
                'valueIngredient_' + value_ingredient
            ]
    return ingredients


@login_required
def new_recipe(request):
    if request.method != 'POST':
        form = RecipeForm()
        return render(request, 'recipe_form.html', {'form': form})

    form = RecipeForm(request.POST, files=request.FILES or None)
    ingredients = get_ingredients(request)

    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        recipe_ingrids = []
        for name, amount in ingredients.items():
            ingredient = get_object_or_404(Ingredient, name=name)
            recipe_ingrids.append(RecipeIngredient(
                recipe=recipe, ingredient=ingredient, amount=amount
            ))
        RecipeIngredient.objects.bulk_create(recipe_ingrids)
        return redirect('index')

    return render(request, 'recipe_form.html', {'form': form})


@login_required
def recipe_edit(request, username, pk):
    instance = get_object_or_404(Recipe, author__username=username, pk=pk)
    if instance.author != request.user:
        return redirect('index')

    form = RecipeForm(request.POST or None, files=request.FILES or None,
                      instance=instance)

    if request.method == 'POST':
        ingredients = get_ingredients(request)
        if form.is_valid():
            recipe = form.save()
            recipe_ingrids = []
            for name, amount in ingredients.items():
                ingredient = get_object_or_404(Ingredient, name=name)
                recipe_ingrids.append(RecipeIngredient(
                    recipe=recipe, ingredient=ingredient, amount=amount
                ))
            RecipeIngredient.objects.bulk_create(recipe_ingrids)
            return redirect('index')

    return render(request, 'edit_recipe.html', {'form': form, 'recipe': instance})


def page_not_found(request, exception):
    return render(request, "404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "500.html", {"email": 'wertyos111@gmail.com'}, status=500)
