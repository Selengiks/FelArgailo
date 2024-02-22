# main_bot.py

from service.bot import bot
from service.logger import start_logger
from service.plugins_manager import load_modules


if __name__ == "__main__":
    start_logger("DEBUG")
    load_modules()

    with bot:
        bot.run_until_disconnected()
