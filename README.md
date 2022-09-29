# Recipes
Telegram bot with recipes

## Setting up your development environment
To run the project on your own, create a `.env` file with the following environment variables:
```text
DJANGO_SECRET_KEY=<YOUR-DJANGO-SECRET-KEY>
TELEGRAM_BOT_TOKEN=<YOUR-TELEGRAM-BOT-TOKEN> | You can find out by creating a bot in @BotFather
```

Then install the dependencies:
```shell
pip install -r requirements.txt
```

Run database migrations:
```shell
python3 recipes_admin_api/manage.py migrate
```

## Add recipes
You can add recipes in admin-panel. Recipe inlcude name, category, description, image, ingredients.

## Launch of the project
This bot works via API with an internal service that runs on Django, so you must always run a django project for the bot to work.
It starts with the following commands:
```shell
python3 recipes_admin_api/manage.py runserver

cd bot
python3 main.py
```
