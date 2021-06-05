from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.views.generic import DetailView, ListView, TemplateView
from django.http.response import Http404
from recipes.forms import RecipeForm
from recipes.models import (Cart, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Tag, User)


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
            context['cart'] = Cart.objects.get_or_create(
                owner=self.request.user)[0]
        return context


class BaseRecipeListView(ListView, IsFavouriteMixin, CartMixin):
    """Base view for Recipe list."""
    context_object_name = 'recipe_list'
    queryset = Recipe.objects.all()
    paginate_by = settings.LIST_OBJECTS
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

        if not tags:
            tags = Tag.objects.values_list('slug')
            tags = [slug for tag in tags for slug in tag]

        qs = qs.filter(tags__slug__in=tags)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = self.request.GET.getlist('tags')
        context['tags'] = tags
        return context


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
    paginate_by = settings.LIST_OBJECTS
    template_name = 'recipes/purchase_list.html'

    def get_queryset(self):
        cart = Cart.objects.get_or_create(owner=self.request.user)[0]
        recipes = cart.recipes.all()
        return recipes


class TechView(TemplateView, CartMixin):
    template_name = 'technologies.html'


class AboutView(TemplateView, CartMixin):
    template_name = 'about_arum.html'


def get_ingredients(request):
    ingredients = {}
    errors = []
    for key in request.POST:
        if key.startswith('nameIngredient'):
            value_ingredient = key[15:]
            name = request.POST[key]
            amount = request.POST[
                'valueIngredient_' + value_ingredient
            ]
            ingredients[name] = amount
            if int(amount) < 1:
                errors.append('Количество должно быть больше 0')

    if not ingredients:
        errors.append('В рецепте должны быть ингридиенты')
    for name in ingredients.keys():
        try:
            get_object_or_404(Ingredient, name=name)
        except Http404:
            errors.append(f'ингридиента {name} не существует')
            return ingredients, errors
    return ingredients, errors


@login_required
def new_recipe(request):
    if request.method != 'POST':
        form = RecipeForm()
        return render(request, 'recipe_form.html', {'form': form})

    form = RecipeForm(request.POST, files=request.FILES or None)
    ingredients, ingrid_errors = get_ingredients(request)

    if ingrid_errors:
        return render(request, 'recipe_form.html', {'form': form,
                                                    'errors': ingrid_errors})

    if form.is_valid():
        tags = form.cleaned_data['tags']
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        recipe_ingrids = []
        for name, amount in ingredients.items():
            ingredient = get_object_or_404(Ingredient, name=name)
            recipe_ingrids.append(RecipeIngredient(
                recipe_id=recipe.id, ingredient=ingredient, amount=amount
            ))
        for tag in tags:
            RecipeTag.objects.get_or_create(recipe_id=recipe.id, tag=tag)
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
    RecipeIngredient.objects.filter(recipe_id=pk).delete()

    if request.method == 'POST':
        ingredients, ingrid_errors = get_ingredients(request)
        if ingrid_errors:
            return render(request, 'recipe_form.html',
                          {'form': form,
                           'recipe': instance,
                           'errors': ingrid_errors})

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

    return render(request, 'edit_recipe.html',
                  {'form': form, 'recipe': instance})


def page_not_found(request, exception):
    return render(request, "404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "500.html",
                  {"email": 'wertyos111@gmail.com'}, status=500)
