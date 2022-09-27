import random

from textwrap import dedent

import requests

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                      ReplyKeyboardMarkup)
from telegram.ext import CallbackContext
from telegram.callbackquery import CallbackQuery
from telegram import ParseMode


def get_random_recipe(
        update: Update,
        context: CallbackContext,
        query: CallbackQuery = None):
    url = "http://127.0.0.1:8000/api/recipe/random/"
    params = {
        "telegram_id": context.user_data["telegram_id"]
    }
    response = requests.get(url, params=params)

    if response.ok:
        recipe = response.json()
        recipe_name = recipe["recipe_name"]
        context.user_data["recipe_name"] = recipe_name
        recipe_description = recipe["recipe_description"]
        recipe_photo_url = recipe["recipe_image"]
        response = requests.get(recipe_photo_url)
        response.raise_for_status()
        recipe_ingredients = [
            f"- {ingredient[0]}" for ingredient in
            recipe["recipe_ingredients"]
        ]
        formatted_ingredients = '\n'.join(recipe_ingredients)

        recipe_message = dedent(f"""\
            <b>{recipe_name}</b>
    
            <b>Описание:</b>
            {recipe_description} 
    
            <b> Ингредиенты: </b>
            {formatted_ingredients} 
            """).replace("  ", "")

        keyboard = [
            [
                InlineKeyboardButton("Лайк", callback_data="like"),
                InlineKeyboardButton("Дизлайк", callback_data="dislike"),
            ],
            [
                InlineKeyboardButton(
                    "Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        if query:
            query.message.reply_photo(
                response.content,
                caption=recipe_message,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
        else:
            update.message.reply_photo(
                response.content,
                caption=recipe_message,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
        return True
    else:
        message_keyboard = [["Назад", "Главное меню"]]
        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True)
        if query:
            query.message.reply_text(
                text="Вы уже просмотрели все рецепты, которые у нас есть!",
                reply_markup=markup
            )
        else:
            update.message.reply_text(
                text="Вы уже просмотрели все рецепты, которые у нас есть!",
                reply_markup=markup
            )

        return False


def get_recipes_in_category(
        update: Update,
        context: CallbackContext,
        query: CallbackQuery,
        category: str):
    url = "http://127.0.0.1:8000/api/category/recipes/"
    params = {
        "category": category,
        "telegram_id": context.user_data["telegram_id"]
    }
    response = requests.get(url, params=params)

    if not response.ok:
        message_keyboard = [["Назад", "Главное меню"]]
        markup = ReplyKeyboardMarkup(message_keyboard,
                                     resize_keyboard=True,
                                     one_time_keyboard=True)
        error_message = dedent("""\
            Подобная категория не найдена.
            """)
        if not query:
            update.message.reply_text(error_message, reply_markup=markup)
        else:
            query.message.reply_text(error_message, reply_markup=markup)
        return False

    recipes_in_category = response.json()
    if not recipes_in_category["available_recipes"]:
        message_keyboard = [["Назад", "Главное меню"]]
        markup = ReplyKeyboardMarkup(message_keyboard,
                                     resize_keyboard=True,
                                     one_time_keyboard=True)
        info_message = dedent("""\
                Вы уже посмотрели все рецепты в этой категории!
                """)
        if not query:
            update.message.reply_text(info_message, reply_markup=markup)
        else:
            query.message.reply_text(info_message, reply_markup=markup)
        return False

    random_recipe = random.choice(recipes_in_category["available_recipes"])
    recipe_name = random_recipe["recipe_name"]
    context.user_data["recipe_name"] = recipe_name
    recipe_description = random_recipe["recipe_description"]
    recipe_photo_url = random_recipe["recipe_photo"]
    response = requests.get(recipe_photo_url)
    response.raise_for_status()

    recipe_ingredients = [
        f"- {ingredient}" for ingredient in random_recipe["recipe_ingredients"]
    ]
    formatted_ingredients = '\n'.join(recipe_ingredients)

    recipe_message = dedent(f"""\
                {recipe_name}
                <b>Описание:</b>
                {recipe_description} 
                <b> Ингредиенты: </b>
                {formatted_ingredients} 
                """).replace("  ", "")

    keyboard = [
        [
            InlineKeyboardButton("Лайк", callback_data="like"),
            InlineKeyboardButton("Дизлайк", callback_data="dislike"),
        ],
        [
            InlineKeyboardButton("Главное меню", callback_data="main_menu")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if not query:
        update.message.reply_photo(
            response.content,
            caption=recipe_message,
            reply_markup=markup,
            parse_mode=ParseMode.HTML)
    else:
        query.delete_message()
        query.message.reply_photo(
            response.content,
            caption=recipe_message,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    return True
