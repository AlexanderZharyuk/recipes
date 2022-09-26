from textwrap import dedent

import requests
from more_itertools.more import chunked
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from bot.states import States


class ButtonName:
    MAIN_MENU = "Главное меню"
    BACK = "Назад"
    

def get_menu_message(ingredients: list, recipe: dict) -> str:
    parsed_ingredients = ""
    for ingredient in ingredients:
        parsed_ingredients += \
            f"{' - '.join([str(item) for item in ingredient])} грамм\n"

    menu_message = dedent(f"""\
                <b>{recipe.get("recipe_name")}</b>

                <b>Ингредиенты:</b>
                {parsed_ingredients}
                <b>Приготовление:</b>
                {recipe.get("recipe_description")}
                """).replace("    ", "")
    
    return menu_message


def get_favorite_recipes(telegram_id: int) -> dict:
    params = {
        "user_telegram_id": telegram_id
    }
    url = "http://127.0.0.1:8000/api/favourites/"
    response = requests.get(url=url, params=params)
    response.raise_for_status()

    return response.json()


def show_favorite_recipes_markup(
        update: Update,
        context: CallbackContext
) -> States:
    """
    Отрисовываем клавиатуру с избранными рецптами пользователя
    """
    telegram_id = update.message.from_user.id
    recipes = get_favorite_recipes(telegram_id)
    favourite_recipes = recipes["favourite_recipes"]
    keyboard = favourite_recipes + [ButtonName.MAIN_MENU]
    message_keyboard = list(chunked(keyboard, 2))

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    if not favourite_recipes:
        update.message.reply_text(
            text="У вас отсутствуют избранные рецепты",
            reply_markup=markup
        )
        return States.USER_RECIPES

    update.message.reply_text(
        text="Ваши предпочтения",
        reply_markup=markup
    )
    return States.USER_RECIPES


def show_favorite_recipe(update: Update, context: CallbackContext) -> States:
    """
    Показывает описание выбранного рецепта с картинкой
    """
    recipe_name = update.message.text
    url = "http://127.0.0.1:8000/api/recipe/"
    params = {
        "recipe_name": recipe_name
    }
    response = requests.get(url, params=params)

    if response.ok:
        recipe = response.json()
        ingredients = recipe.get("recipe_ingredients")
        menu_message = get_menu_message(
            recipe=recipe,
            ingredients=ingredients
        )
        message_keyboard = [
            [
                ButtonName.BACK,
                ButtonName.MAIN_MENU
            ]
        ]
        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        recipe_img = requests.get(recipe["recipe_image"])
        update.message.reply_photo(
            recipe_img.content,
            caption=menu_message,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    else:
        update.message.reply_text("Такого рецепта нет 😥")
    return States.FAVORITE_RECIPE