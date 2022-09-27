from django.contrib import admin

from .models import Recipe, Ingredient, Category, User, IngredientsInRecipe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


class RecipeInline(admin.TabularInline):
    model = IngredientsInRecipe
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeInline
    ]
    filter_horizontal = ['favourite_in', 'dislike']


@admin.register(Ingredient)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class IngredientAdmin(admin.ModelAdmin):
    pass
