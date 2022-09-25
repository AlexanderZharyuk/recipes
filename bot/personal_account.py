from textwrap import dedent

import requests
from more_itertools.more import chunked
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from bot.states import States


def get_favorite_recipes(update: Update, context: CallbackContext) -> States:
    """
    Отрисовываем клавиатуру с избранными рецптами пользователя
    """
    telegram_id = update.message.from_user.id

    params = {
        "user_telegram_id": telegram_id
    }
    url = "http://127.0.0.1:8000/api/favourites/"
    response = requests.get(url=url, params=params)

    favourite_recipes = response.json()['favourite_recipes']
    keyboard = favourite_recipes + ['Главное меню']
    message_keyboard = list(chunked(keyboard, 2))

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    if not favourite_recipes:
        update.message.reply_text(
            text='У вас отсутствуют избранные рецепты',
            reply_markup=markup
        )
        return States.USER_RECIPES

    update.message.reply_text(
        text='Ваши предпочтения',
        reply_markup=markup
    )
    return States.USER_RECIPES


def show_favorite_recipe(update: Update, context: CallbackContext) -> States:
    """
    Показывает описание выбранного рецепта с картинкой
    """
    recipe_name = update.message.text
    url = 'http://127.0.0.1:8000/api/recipe/'
    params = {
        "recipe_name": recipe_name
    }
    response = requests.get(url, params=params)

    if response.ok:
        recipe = response.json()
        ingredients = recipe.get('recipe_ingredients')
        parsed_ingredients = ""
        for ingredient in ingredients:
            parsed_ingredients += \
                f"{' - '.join([str(item) for item in ingredient])} грамм\n"

        menu_msg = dedent(f"""\
            <b>{recipe.get('recipe_name')}</b>

            <b>Ингредиенты:</b>
            {parsed_ingredients}
            <b>Приготовление:</b>
            {recipe.get('recipe_description')}
            """).replace("    ", "")

        message_keyboard = [
            [
                "Назад",
                "Главное меню"
            ]
        ]
        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        recipe_img = requests.get(recipe['recipe_image'])
        update.message.reply_photo(
            recipe_img.content,
            caption=menu_msg,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    else:
        update.message.reply_text('Такого рецепта нет 😥')
    return States.FAVORITE_RECIPE