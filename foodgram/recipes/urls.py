from django.conf.urls import url
from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from recipes import views
from recipes.api import views as api

views_patterns = [
    path('',
         views.IndexView.as_view(), name='index'),
    path('favourites/',
         views.FavouriteView.as_view(), name='favourites'),
    path('profiles/<str:username>/',
         views.ProfileView.as_view(), name='profile'),
    path('recipes/create/', views.new_recipe, name='create'),
    path('edit/<str:username>/<int:pk>/', views.recipe_edit, name='edit'),
    path('recipes/<int:pk>/',
         views.RecipeDetailView.as_view(), name='recipe'),
    path('subscriptions/', views.MyFollowingsView.as_view(),
         name='subscriptions'),
    path('purchases/', views.MyCartView.as_view(), name='purchases'),
    url(r'^download/', views.download_purchases, name='download'),
]

api_patterns = [
    path('ingredients/', api.GetIngredients.as_view()),
    path('favourites/',
         api.AddToFavorites.as_view()),
    path('favourites/<int:pk>/',
         api.RemoveFromFavorites.as_view()),
    path('subscriptions/', api.Subscribe.as_view()),
    path('subscriptions/<int:pk>/', api.UnSubscribe.as_view()),
    path('purchases/', api.AddPurchase.as_view()),
    path('purchases/<int:pk>/', api.RemoveFromPurchases.as_view(),
         name='delete_purchase'),
]

urlpatterns = [
    path('', include(views_patterns)),
    path('api/', include(format_suffix_patterns(api_patterns))),
]
