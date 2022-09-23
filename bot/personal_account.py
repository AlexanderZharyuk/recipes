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
        return States.USER_RECIPE
    else:
        update.message.reply_text('У вас отсутствуют избранные рецепты')


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
