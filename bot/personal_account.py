import logging

from textwrap import dedent
from enum import Enum, auto

import environs
import requests

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (CallbackQueryHandler, CallbackContext,
                          CommandHandler, ConversationHandler,
                          MessageHandler, Filters, Updater)


class States(Enum):
    USER_RECIPE = auto()


def get_favorite_recipes(update: Update, context: CallbackContext) -> States:
    """
    Отрисовываем клавиатуру с избранными рецптами пользователя
    """
    telegram_id = update.message.from_user.id
    params = {
        'user_telegram_id': telegram_id
    }

    # url = "http://127.0.0.1:8000/api/favourites/"
    # favorite_recipes = requests.get(url=url, params=params)
    # recipes = favorite_recipes.get('recipes')
    favorite_recipes = 1
    recipes = [['sfdsfds', 'ssssvv']]

    if favorite_recipes.ok:
        message_keyboard = [recipes]
        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True)
        update.message.reply_text(reply_markup=markup)
        return States.USER_RECIPE
    else:
        update.message.reply_text('У вас отсутствуют избранные рецепты')


def show_recipe(update: Update, context: CallbackContext) -> States:
    """
    Показывает описание выбранного рецепта с картинкой
    """
    pass
    # response = requests.get()

    # recipe = {
    #     "name": "Салат с красной фасолью консервированной и курицей",
    #     "category": "Диетическая",
    #     "image": dish_img,
    #     "description": dish_description
    # }
    # message_keyboard = [['Назад', 'Главное меню']]
    # markup = ReplyKeyboardMarkup(message_keyboard,
    #                              resize_keyboard=True,
    #                              one_time_keyboard=True)
    # menu_msg = dedent(f"""
    # Наименование:
    #     {recipe.get('name')},
    # Категория:
    #     {recipe.get('category')},
    # Приготовление:
    #     {recipe.get('description')},
    # """)
    # update.message.


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
        entry_points=[CommandHandler("start", get_favorite_recipes)],
        states={
            States.USER_RECIPE: [
                MessageHandler(
                    Filters.text, show_recipe
                )
            ]
        },
        fallbacks=[],
        allow_reentry=True,
        name='bot_conversation'
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
