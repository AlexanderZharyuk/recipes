import os
import time

import telegram
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

# from bot.models import Block, Flow, Flow_group, Presentation, Speaker

###################
# Новый рецепт #
###################

def main_keyboard(update, context):
    keyboard = [
        [
            InlineKeyboardButton('📋 Новый рецепт',
                                 callback_data='New_recipe'),
            InlineKeyboardButton('🗣 Личный кабинет',
                                 callback_data='Personal')
        ]
    ]
    context.bot.send_message(
        update.effective_chat.id,
        'Главное меню',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def categories_keyboard(update, context):
    keyboard = [
        [InlineKeyboardButton('Веганство', callback_data='Vegan'), InlineKeyboardButton('Спортивное',
                                 callback_data='Sport')],
        [InlineKeyboardButton('Диетическое', callback_data='Diet'), InlineKeyboardButton('Без калорий',
                                                                                        callback_data='No_calories')],
        [InlineKeyboardButton('Случайный рецепт', callback_data='Random_recipe')],
        [InlineKeyboardButton('📍 Главное меню', callback_data='Main_menu')]
    ]

    context.bot.send_message(update.effective_chat.id,
                             'Категории',
                             reply_markup=InlineKeyboardMarkup(keyboard))


def button(update, context):
    q = update.callback_query
    q.answer()
    if q.data == 'New_recipe':
        return categories_keyboard(update, context)
    elif q.data == 'Personal':
        pass
    elif q.data == 'Vegan':
        pass
    elif q.data == 'Diet':
        pass
    elif q.data == 'No_calories':
        pass
    elif q.data == 'Random_recipe':
        pass
    elif q.data == 'Main_menu':
        return main_keyboard(update, context)


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("TG_BOT_TOKEN")
    bot = telegram.Bot(token=token)
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    main_keyboard_handler = CommandHandler('main', main_keyboard)
    dispatcher.add_handler(main_keyboard_handler)

    button_handler = CallbackQueryHandler(button)
    dispatcher.add_handler(button_handler)

    updater.start_polling()

    updater.idle()
