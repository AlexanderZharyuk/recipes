import random

from textwrap import dedent

from django.http.response import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from .models import User, Favourites, Category, Recipe


def get_user(request, telegram_id) -> JsonResponse:
    """
    Получение данных о пользователе, если пользователя
    нет в БД - выбрасывает 502 статус ответа
    """
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except ObjectDoesNotExist:
        response = {
            'status': 'false',
            'message': 'user not found'}
        return JsonResponse(response, status=502)

    response = {
        'user_id': user.telegram_id,
        'user_fullname': user.fullname,
        'user_phone_number': user.phone_number
    }
    return JsonResponse(
        response,
        status=200,
        json_dumps_params={'ensure_ascii': False}
    )


@csrf_exempt
def add_user(request) -> JsonResponse:
    """
    Добавление юзера в БД с полученными данными от ТГ-бота.
    """
    if request.method == 'POST':
        user_telegram_id = request.POST.get('user_tg_id')
        user_fullname = request.POST.get('user_fullname')
        user_phone_number = request.POST.get('user_phone_number')

        user = User.objects.create(
            telegram_id=user_telegram_id,
            fullname=user_fullname,
            phone_number=user_phone_number
        )

        Favourites.objects.create(user=user)

        response = {
            'status': 'true',
            'message': 'user created'
        }
        return JsonResponse(response, status=200)

    response = {
        'status': 'false',
        'message': 'Not supported method'
    }
    return JsonResponse(response, status=501)


def get_categories(request) -> JsonResponse:
    """
    Выдаем список доступных категорий.
    """
    categories = [category.name for category in Category.objects.all()]
    response = {
        "available_categories": categories
    }

    if not categories:
        response = {
            "status": False,
            "message": "Not found categories. "
                       "Please, add categories in admin panel"
        }
        return JsonResponse(data=response, status=503)

    return JsonResponse(
        data=response,
        status=200,
        json_dumps_params={'ensure_ascii': False}
    )


def get_recipes_in_category(request) -> JsonResponse:
    """
    Получение рецептов в категории.
    В виде пареметров нужно передать словарь:
    {
        'category': category_name,
        'telegram_id': telegram_id
    }
    """
    category_name = request.GET.get('category')
    telegram_id = request.GET.get('telegram_id')
    recipes = Recipe.objects.select_related('category')\
        .filter(category__name=category_name)

    if not recipes:
        response = {
            'status': 'False',
            'message': 'Not found category'
        }
        return JsonResponse(data=response, status=502)

    user = Favourites.objects.get(user__telegram_id=telegram_id)
    user_favourites = user.recipes.all()

    available_recipes = [
        {
            'recipe_name': recipe.name,
            'recipe_description': recipe.description,
            'recipe_photo': request.build_absolute_uri(recipe.image.url),
            'recipe_ingredients': [
                item.ingredient.name for item
                in recipe.ingredients.all()
            ],
        }
        for recipe in recipes if recipe not in user_favourites
    ]

    if not available_recipes:
        available_recipes = None

    response = {
        'category': category_name,
        'available_recipes': available_recipes,
    }
    return JsonResponse(
        response,
        status=200,
        json_dumps_params={'ensure_ascii': False}
    )


def get_recipe(request) -> JsonResponse:
    """
    Получение информации о рецепте.
    В виде пареметров нужно передать словарь:
    {
        'recipe_name': recipe_name
    }
    """
    # TODO пределать вьюху - если нет в избранном у пользователя, то ошибка
    recipe_name = request.GET.get('recipe_name')
    recipe = Recipe.objects.get(name=recipe_name)

    response = {
        'recipe_name': recipe.name,
        'recipe_description': recipe.description,
        'recipe_image': request.build_absolute_uri(recipe.image.url),
        'recipe_ingredients': [
            [item.ingredient.name, item.quantity]
            for item
            in recipe.ingredients.all()
        ],
    }
    return JsonResponse(
        response,
        status=200,
        json_dumps_params={'ensure_ascii': False}
    )


def get_random_recipe(request) -> JsonResponse:
    """
    Получение рандомного рецепта.
    """
    recipes = Recipe.objects.all()
    telegram_id = request.GET.get('telegram_id')
    user = Favourites.objects.get(user__telegram_id=telegram_id)
    user_favourites = user.recipes.all()

    available_recipes = list(set(recipes) - set(user_favourites))
    if not available_recipes:
        response = {
            'status': 'False',
            'message': 'Not available recipes for user'
        }
        return JsonResponse(data=response, status=502)

    random_recipe = random.choice(available_recipes)

    if random_recipe not in user_favourites:
        response = {
            'recipe_name': random_recipe.name,
            'recipe_description': random_recipe.description,
            'recipe_image': request.build_absolute_uri(random_recipe.image.url),
            'recipe_ingredients': [
                [
                    item.ingredient.name,

                ] for item
                in random_recipe.ingredients.all()
            ],
        }
        return JsonResponse(
            response,
            status=200,
            json_dumps_params={'ensure_ascii': False}
        )


@csrf_exempt
def add_to_favourite(request) -> JsonResponse:
    """
    Если пользователь лайкнул рецепт - добавляем его к нему в избранные
    """
    if request.method == 'POST':
        user_telegram_id = request.POST.get('user_tg_id')
        recipe_name = request.POST.get('recipe_name')

        user = User.objects.get(telegram_id=user_telegram_id)
        recipe = Recipe.objects.get(name=recipe_name)
        user_favourites = Favourites.objects.get(user=user)
        user_favourites.recipes.add(recipe)

        response = {
            'status': 'true',
            'message': f'add recipe to user-{user_telegram_id} favourites'
        }
        return JsonResponse(response, status=200)

    response = {
        'status': 'false',
        'message': 'Not supported method'
    }
    return JsonResponse(response, status=501)


def get_user_favourites(request) -> JsonResponse:
    """
    Выдаем лайкнутые пользователем рецепты.
    Принимает словарь с GET-параметрами:
    {
        user_telegram_id: telegram_id: int
    }
    """
    user_telegram_id = request.GET.get('user_telegram_id')
    user_favourites = Favourites.objects.get(
        user__telegram_id=user_telegram_id
    )
    response = {
        'favourite_recipes': [
            recipe.name for recipe in user_favourites.recipes.all()
        ]
    }
    return JsonResponse(
        response,
        status=200,
        json_dumps_params={'ensure_ascii': False}
    )
