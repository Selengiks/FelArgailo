# main_bot.py

from service.bot import bot
from service.logger import start_logger
from service.plugins_manager import PluginManager
from service.scheduler import start_scheduler


if __name__ == "__main__":
    start_logger("DEBUG")
    PluginManager.load_modules()
    start_scheduler()

    with bot:
        bot.run_until_disconnected()
