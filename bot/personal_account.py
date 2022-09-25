import logging

from textwrap import dedent
from enum import Enum, auto

import environs
import requests

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                      ReplyKeyboardMarkup, KeyboardButton, ParseMode)
from telegram.ext import (CallbackQueryHandler, CallbackContext,
                          CommandHandler, ConversationHandler,
                          MessageHandler, Filters, Updater)


class States(Enum):
    USER_RECIPES = auto()
    FAVORITE_RECIPE = auto()


def get_favorite_recipes_markup(update: Update, context: CallbackContext) -> States:
    """
    Отрисовываем клавиатуру с избранными рецптами пользователя
    """
    telegram_id = update.message.from_user.id
    params = {
        "user_telegram_id": telegram_id
    }

    url = "http://127.0.0.1:8000/api/favourites/"
    response = requests.get(url=url, params=params)

    if response.ok:
        message_keyboard = [response.json()['favourite_recipes']]
        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True)
        update.message.reply_text(text='Ваши предпочтения', reply_markup=markup)
    else:
        update.message.reply_text('У вас отсутствуют избранные рецепты')
    return States.USER_RECIPES


def show_favorite_recipe(update: Update, context: CallbackContext) -> States:
    """
    Показывает описание выбранного рецепта с картинкой
    """
    recipe_name = update.message.text
    print(recipe_name)
    url = 'http://127.0.0.1:8000/api/recipe/'
    params = {
        "recipe_name": recipe_name
    }
    response = requests.get(url, params=params)

    if response.ok:
        recipe = response.json()
        menu_msg = dedent(f"""\
            <b>{recipe.get('recipe_name')}</b>
            
            <b>Ингредиенты:</b>
            {recipe.get('recipe_ingredients')},
            
            <b>Приготовление:</b>
            {recipe.get('recipe_description')},
            """).replace("    ", "")

        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data="back"),
            ],
            [
                InlineKeyboardButton("Главное меню", callback_data="main_menu")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        recipe_img = requests.get(recipe['recipe_image'])
        update.message.reply_photo(
            recipe_img.content,
            caption=menu_msg,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    else:
        update.message.reply_text('Такого рецепта нет 😥')
    return States.USER_RECIPES


if __name__ == '__main__':
    env = environs.Env()
    env.read_env()
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    telegram_bot_token = env.str("TELEGRAM_BOT_TOKEN")

    updater = Updater(telegram_bot_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", get_favorite_recipes_markup)],
        states={
            States.USER_RECIPES: [
                MessageHandler(
                    Filters.text, show_favorite_recipe
                )
            ],
            States.FAVORITE_RECIPE: [
                CallbackQueryHandler(
                    show_favorite_recipe, pattern="back"
                ),
                CallbackQueryHandler(
                    show_favorite_recipe, pattern="main_menu"
                ),
            ]
        },
        fallbacks=[],
        allow_reentry=True,
        name='bot_conversation'
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
