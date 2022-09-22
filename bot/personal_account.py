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


def get_list_of_recipes(update: Update, context: CallbackContext) -> States:
    """
    Отрисовываем клавиатуру с избранными рецптами пользователя
    """
    telegram_id = update.message.from_user.id
    """"
    Пример списка избранных рецептов пользователя
    """
    user_recipes = {
        "user": telegram_id,
        "recipes": [
            "Салат с красной фасолью консервированной и курицей",
            "Запеченные креветки с сыром ПП",
            "Овсяноблин на завтрак для правильного питания ПП",
            "Салат с белой фасолью консервированной огурцом и курицей",
            "Ленивая овсянка в банке с йогуртом",
            "Яблоки с медом запеченные в микроволновке целиком в кожуре",
            "ПП салат с тунцом консервированным жульеном",

        ]
    }
    recipes = list(user_recipes.get('recipes'))
    message_keyboard = [recipes]

    markup = ReplyKeyboardMarkup(message_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)

    update.message.reply_document(reply_markup=markup)
    return States.USER_RECIPE


def show_recipe(update: Update, context: CallbackContext) -> States:
    """
    Показывает описание выбранного рецепта с картинкой
    """
    dish_img = open('salat-s-krasnoi-fasolu-konservirovannoi-i-kuricei_1602137970_10_max.jpg', 'rb')
    dish_description = dedent("""
    Как сделать салат из красной фасоли? Подготовьте ингредиенты. Куриную грудку можно отварить заранее или использовать от ранее приготовленного блюда из курицы. Фасоль и кукуруза консервированные. Перец болгарский один большой или два маленьких. Лук салатный красный. Для заправки салата можно использовать рекомендованную заправку или просто оливковое масло. Соль возьмите по вкусу, также можно добавить чёрный молотый перец.
    Возьмите глубокую посуду для салата - миску, салатник. Охлаждённую куриную грудку без кости порежьте маленькими кубиками и выложите в салатник.
    Банку с консервированной красной фасолью осторожно откройте, слейте жидкость, а фасоль промойте холодной водой. Выложите в салатник нужное количество фасоли. Для салата также можно взять отварную красную фасоль.
    Банку с консервированной кукурузой осторожно откройте, слейте жидкость. Добавьте в салатник нужное количество кукурузы.
    Красный болгарский перец помойте, срежьте плодоножку и освободите его от семян. Промойте перец холодной водой внутри и снаружи. Стряхните плоды от лишней жидкости и нарежьте перец небольшими кубиками. Добавьте нарезанный перец в салат.
    Салатный лук очистите от шелухи и порежьте маленьким кубиками. Добавьте его в салат.
    Свежую зелень петрушки промойте проточной холодной водой и обсушите. Нарежьте мелко зелень и добавьте в салат. Также по вкусу можете добавить или укроп, или кинзу, или смесь свежей зелени.
    Для заправки салата в миске смешайте растительное масло (я взяла виноградное), яблочный уксус и готовую горчицу (у меня русская, но вкусно будет и с дижонской). Соль и чёрный молотый перец можно добавить в заправку, а можно добавить непосредственно в сам салат. Заправьте салат подготовленной заправкой и перемешайте. Попробуйте ещё раз на соль и при необходимости подсолите.
    Готовый салат можно подавать сразу по его приготовлению, но более насыщенный вкус будет у салата если он немного постоит в холодильнике перед подачей на стол. Салат можно предложить как самостоятельное блюдо, а можно разнообразить им стол с блюдами из картофеля.
    """)

    recipe = {
        "name": "Салат с красной фасолью консервированной и курицей",
        "category": "Диетическая",
        "image": dish_img,
        "description": dish_description
    }
    message_keyboard = [['Назад', 'Главное меню']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    menu_msg = dedent(f"""
    Наименование: 
        {recipe.get('name')},
    Категория: 
        {recipe.get('category')},
    Приготовление: 
        {recipe.get('description')},
    """)
    update.message.

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
        entry_points=[CommandHandler("start", get_list_of_recipes)],
        states={
            States.USER_RECIPE: [
                MessageHandler(
                    Filters.text, show_recipe
                )
            ]
        }
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
