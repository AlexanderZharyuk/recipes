# recipes
Телеграм-бот с рецептами

## Предустановка
Для того, чтобы запустить проект у себя, создайте `.env`-файл со следующими переменными окружения:
```text
DJANGO_SECRET_KEY=<YOUR-DJANGO-SECRET-KEY>
TELEGRAM_BOT_TOKEN=<YOUR-TELEGRAM-BOT-TOKEN> | Узнать можно создав бота в @BotFather
```

После чего установите зависимости:
```shell
pip install -r requirements.txt
```

Выполните миграции для БД:
```shell
python3 recipes_admin_api/manage.py migrate
```

## Запуск проекта
Данный бот работает по API с внутренним сервисом, который запускается на Django, поэтому необходимо всегда запускать джанго проект для работы бота.
Запуск происходит следующими командами:
```shell
python3 recipes_admin_api/manage.py runserver
python3 bot/main.py
```

# Бизнес-логика бота
![diagram (2)](https://user-images.githubusercontent.com/46388832/191375039-ce859da0-20be-463d-b127-a6c67136cb34.png)
