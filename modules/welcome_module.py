from telethon import events
from service.bot import bot
from service.plugins_manager import PluginManager
from service.help_manager import HelpManager
from loguru import logger


def get_help_text():
    return (
        "**Примітка**:\n"
        "    -__Щоб вкрасти медіа з дефолтним підписом, але іншим тегом, введи `!ssteal #tag`.__\n"
        "    -__Можна ввести множину тегів, наприклад `!ssteal #tag1 tag2`.__\n"
        "    -__Пожалійте сервер і Фелікса, не зловживайте закачкою відосів у макc. якості.__"
    )


def start_module():
    logger.info("Welcome module started")

    @bot.on(events.NewMessage(pattern="!sstatus"))
    async def send_welcome(event):
        successful_modules = PluginManager.get_successful_modules()
        problematic_modules = PluginManager.get_problematic_modules()
        disabled_modules = PluginManager.get_disabled_modules()

        num_successful_modules = len(successful_modules)
        num_problematic_modules = len(problematic_modules)
        num_disabled_modules = len(disabled_modules)

        message = (
            "**Кібер-Фелікс**:\n"
            "__Модуль ШІ для автоматизації шітпостингу активовано.__\n\n"
            "**Підключені модулі:**\n"
            f"`{', '.join(successful_modules.keys()) if num_successful_modules else 'Немає підключених модулів'}`\n\n"
            "**Вимкнені модулі:**\n"
            f"`{', '.join(disabled_modules) if num_disabled_modules else 'Немає вимкнених модулів'}`\n\n"
            "**Проблемні модулі:**\n"
            f"`{', '.join(f'{module} ({error})' for module, error in problematic_modules) if num_problematic_modules else 'Немає проблемних модулів'}`\n\n"
        )

        await event.reply(message)

    @bot.on(events.NewMessage(pattern="!hhelp"))
    async def felix_help(event):
        await event.reply(HelpManager.get_help())
