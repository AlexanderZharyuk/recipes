import logging

from textwrap import dedent
from enum import Enum, auto

import environs
import requests
import phonenumbers

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (CallbackQueryHandler, CallbackContext,
                          CommandHandler, ConversationHandler,
                          MessageHandler, Filters, Updater)
from telegram import ParseMode
from more_itertools import chunked


class States(Enum):
    ACCEPT_PRIVACY = auto()
    START_REGISTRATION = auto()
    USER_FULLNAME = auto()
    USER_PHONE_NUMBER = auto()
    MAIN_MENU = auto()
    CATEGORY = auto()


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> States:
    """
    Старт бота - если юзер есть в БД, то выкидываем в главное меню,
    иначе предлагаем принять оферту об обработке данных.
    """
    telegram_id = update.message.from_user.id
    url = f"http://127.0.0.1:8000/api/users/{telegram_id}"
    response = requests.get(url)

    if response.ok:
        user = response.json()
        user_fullname = user["user_fullname"]
        message_keyboard = [["🍳 Рецепты", "🙇🏻 Личный кабинет"]]
        markup = ReplyKeyboardMarkup(message_keyboard,
                                     resize_keyboard=True,
                                     one_time_keyboard=True)
        menu_msg = dedent(f"""\
        Здравствуй, {user_fullname}!
        
        Найдем новые рецепты или приготовим, что уже пробовали?
        """)
        update.message.reply_text(text=menu_msg, reply_markup=markup)
        return States.MAIN_MENU

    message_keyboard = [['✅ Согласен', '❌ Не согласен']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)

    with open('documents/privacy_policy_statement.pdf', 'rb') as image:
        user_agreement_pdf = image.read()

    greeting_msg = dedent("""\
    Привет!✌️
    
    Для того, чтобы использовать нашего бота - вам необходимо дать согласие \
    на обработку данных. 
    
    Это обязательная процедура, пожалуйста, ознакомьтесь с документом.
    """).replace("  ", "")
    update.message.reply_document(user_agreement_pdf,
                                  filename="Соглашение на обработку "
                                           "персональных данных.pdf",
                                  caption=greeting_msg,
                                  reply_markup=markup)
    return States.ACCEPT_PRIVACY


def cancel_agreement(update: Update, context: CallbackContext) -> States:
    """
    Ответ пользователю, если он не согласен с офертой.
    """
    response_msg = dedent("""\
    К сожалению, тогда мы не сможем дать вам возможность пользоваться нашим \
    ботом. 
    
    Если вы передумали - нажмите на кнопку согласия ниже.
    """).replace("  ", "")

    message_keyboard = [['✅ Согласен', '❌ Не согласен']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)

    update.message.reply_text(
        text=response_msg,
        reply_markup=markup
    )
    return States.ACCEPT_PRIVACY


def start_user_registration(
        update: Update,
        context: CallbackContext) -> States:
    """
    Начало регистрации и сбора данных о пользователе
    """
    update.message.reply_text("👤 Пожалуйста, напишите свое имя и фамилию:")
    return States.START_REGISTRATION


def get_user_fullname(update: Update, context: CallbackContext) -> States:
    """
    Записываем имя пользователя во временный словарь context.user_data для
    будущей записи в БД.
    """
    words_in_user_answer = len(update.message.text.split())
    if words_in_user_answer == 1 or words_in_user_answer > 2:
        update.message.reply_text(dedent("""\
        Некорректный ввод. Может вы забыли указать фамилию?
        
        Попробуйте еще раз:
        """))
        return States.START_REGISTRATION

    context.user_data["fullname"] = update.message.text.title()

    message_keyboard = [
        [
            KeyboardButton(
                'Отправить свой номер телефона',
                request_contact=True)
        ]
    ]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        one_time_keyboard=True,
        resize_keyboard=True)

    update.message.reply_text(
        dedent("""\
        📱 Введите ваш номер телефона в формате \
        <code>+7999-111-22-33</code> или нажмите на кнопку ниже:
        """).replace("  ", ""),
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )
    return States.USER_PHONE_NUMBER


def get_user_phone_number(update: Update, context: CallbackContext) -> States:
    """
    Получаем номер телефона пользователя и проверяем его на валидность.
    Если телефон валидный - отправляем запрос к БД, сохраняем юзера и
    перекидываем в главное меню
    """
    if update.message.contact:
        context.user_data["phone_number"] = update.message.contact.phone_number
    else:
        phone_number = phonenumbers.parse(update.message.text, "RU")
        if not phonenumbers.is_valid_number(phone_number):
            message_keyboard = [
                [
                    KeyboardButton(
                        'Отправить свой номер телефона',
                        request_contact=True)
                ]
            ]
            markup = ReplyKeyboardMarkup(
                message_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True)
            error_message = dedent("""\
            Введенный номер некорректен. Попробуйте снова:
            """)
            update.message.reply_text(error_message, reply_markup=markup)
            return States.USER_PHONE_NUMBER

        context.user_data["phone_number"] = update.message.text

    user_telegram_id = update.message.from_user.id
    url = f"http://127.0.0.1:8000/api/users/add/"
    payload = {
        "user_tg_id": user_telegram_id,
        "user_fullname": context.user_data["fullname"],
        "user_phone_number": context.user_data["phone_number"]
    }
    response = requests.post(url, data=payload)

    if response.ok:
        message_keyboard = [["🍳 Рецепты", "🙇🏻 Личный кабинет"]]
        markup = ReplyKeyboardMarkup(message_keyboard,
                                     resize_keyboard=True,
                                     one_time_keyboard=True)
        end_registration_msg = dedent("""\
        🎉 Регистрация прошла успешно! 
        
        🍳 Для того, чтобы найти новые рецепты - используйте кнопку с \
        рецептами снизу. 
        
        🙇🏻 В вашем личном кабинете будут рецепты, которые вы лайкните.
        """).replace("  ", "")
        update.message.reply_text(end_registration_msg, reply_markup=markup)
        return States.MAIN_MENU

    error_registration_msg = dedent("""\
    Что-то пошло не так, попробуйте снова, нажав /start
    """)
    update.message.reply_text(error_registration_msg)


def categories_keyboard(update: Update, context: CallbackContext) -> States:
    """
    Отрисовываем клавиатуру с рецептами
    """
    # TODO Получить этот список через API
    categories = [
        "Веганство",
        "Спортивное",
        "Диетическое",
        "Без калорий",
        "Случайный рецепт",
        "Главное меню"
    ]
    message_keyboard = list(chunked(categories, 2))
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    categories_msg = dedent("""\
            Выберите из какой категории вы хотели бы получить рецепт.
            """)
    update.message.reply_text(categories_msg, reply_markup=markup)
    return States.CATEGORY


def show_recipe(update: Update, context: CallbackContext):
    """
    Показываем пользователю рецепт из определенной категории
    """
    update.message.reply_text("Пока здесь ничего нет")


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
        entry_points=[CommandHandler("start", start)],
        states={
            States.ACCEPT_PRIVACY: [
                MessageHandler(
                    Filters.text("✅ Согласен"), start_user_registration
                ),
                MessageHandler(
                    Filters.text("❌ Не согласен"), cancel_agreement
                ),
            ],
            States.START_REGISTRATION: [
                MessageHandler(
                    Filters.text, get_user_fullname
                )
            ],
            States.USER_PHONE_NUMBER: [
                MessageHandler(
                    Filters.text, get_user_phone_number
                ),
                MessageHandler(
                    Filters.contact, get_user_phone_number
                )
            ],
            States.MAIN_MENU: [
                MessageHandler(
                    Filters.text("🍳 Рецепты"), categories_keyboard
                ),
                MessageHandler(
                    Filters.text("🙇🏻 Личный кабинет"), show_recipe
                )
            ],
            States.CATEGORY: [
                MessageHandler(
                    Filters.text("Веганство"), show_recipe
                ),
                MessageHandler(
                    Filters.text("Спортивное"), show_recipe
                ),
                MessageHandler(
                    Filters.text("Диетическое"), show_recipe
                ),
                MessageHandler(
                    Filters.text("Без калорий"), show_recipe
                ),
                MessageHandler(
                    Filters.text("Случайный рецепт"), show_recipe
                ),
                MessageHandler(
                    Filters.text("Главное меню"), start
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
