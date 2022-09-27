from django.urls import path

from .views import (get_user, add_user, get_categories, get_recipe,
                    add_to_favourite, get_user_favourites,
                    get_recipes_in_category, get_random_recipe,
                    add_to_dislikes)


urlpatterns = [
    path('users/<int:telegram_id>', get_user),
    path('users/add/', add_user),

    path('categories/', get_categories),
    path('category/recipes/', get_recipes_in_category),

    path('recipe/random/', get_random_recipe),

    path('favourites/recipe/', get_recipe),
    path('favourites/', get_user_favourites),
    path('favourites/add', add_to_favourite),

    path('dislikes/add', add_to_dislikes)
]