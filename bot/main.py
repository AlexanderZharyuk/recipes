import environs


if __name__ == '__main__':
    env = environs.Env()
    env.read_env()

    telegram_bot_token = env.str('TELEGRAM_BOT_TOKEN')