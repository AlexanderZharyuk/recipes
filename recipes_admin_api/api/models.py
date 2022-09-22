from django.db import models
from django.core.validators import MinValueValidator


class User(models.Model):
    telegram_id = models.IntegerField(
        verbose_name='Телеграм ID юзера'
    )
    fullname = models.CharField(
        max_length=30,
        verbose_name='Имя и фамилия пользователя'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Телефон пользователя'
    )

    class Meta:
        db_table = 'user'
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.fullname}'


class Favourites(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favourites',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'favourites'
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'

    def __str__(self):
        return f'{self.user.fullname}'


class Category(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Название категории'
    )

    class Meta:
        db_table = 'category'
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Название рецепта'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True
    )
    image = models.ImageField(
        upload_to='recipes_images',
        verbose_name='Картинка рецепта'
    )
    description = models.TextField(
        verbose_name='Описание рецепта'
    )
    favourite_in = models.ManyToManyField(
        Favourites,
        verbose_name='В избранном',
        related_name='recipes',
        blank=True,
    )

    class Meta:
        db_table = 'recipe'
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=80,
        verbose_name='Наименование ингредиента'
    )

    class Meta:
        db_table = 'ingredient'
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name}'


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты в рецепте',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        verbose_name='Количество в граммах',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = 'ingredients_in_recipe'
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.ingredient.name}'
