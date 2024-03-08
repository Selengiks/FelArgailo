# modules/welcome_module.py

from telethon import events
from service.bot import bot
from service.plugins_manager import PluginManager
from loguru import logger


def start_module():
    logger.info("Welcome module started")

    @bot.on(events.NewMessage(pattern="!status"))
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
            f"`{', '.join(successful_modules) if num_successful_modules else 'Немає підключених модулів'}`\n\n"
            "**Вимкнені модулі:**\n"
            f"`{', '.join(disabled_modules) if num_disabled_modules else 'Немає вимкнених модулів'}`\n\n"
            "**Проблемні модулі:**\n"
            f"`{', '.join(f'{module} ({error})' for module, error in problematic_modules) if num_problematic_modules else 'Немає проблемних модулів'}`\n\n"
        )

        await event.reply(message)

    @bot.on(events.NewMessage(pattern="!help"))
    async def felix_help(event):
        message = (
            "**Кібер-Фелікс**:\n"
            "**Stealer** - __щоб вкрасти мем, чи арт, введи команду `!ssteal` у відповідь на медіа, яке хочеш вкрасти, "
            "тоді медіа буде вкрадено на канал. За замовчуванням, ставиться тег #meme. Щоб керувати командою, "
            "є спеціальні прапори:__\n"
            "    `-q` - __краде медіа із оригінальним підписом, і кидає як цитування.__\n"
            '    `-r` "текст"- __краде медіа з текстом, який введеться після команди.__ '
            "__Наприклад, команда `!ssteal -r Приклад коментаря з тегом #tag`, "
            "вкраде медіа на канал із підписом `Приклад коментаря з тегом #tag`.__\n"
            "    `-g` - __дозволяє вкрасти множину медіа (якщо користувач скинув групу медіа).__\n\n"
            "Додана підтримка реакцій. Щоб вкрасти мем, постав реакцію 🙏. Щоб вкрасти cunny - став 😭\n\n"
            "**Примітка**:\n"
            "    -__Щоб вкрасти медіа з дефолтним підписом, але іншим тегом, введи `!ssteal #tag`.__\n"
            "    -__Можна ввести множину тегів, наприклад `!ssteal #tag1 tag2`.__\n"
            "    -__Прапор можна ставити в будь-якому місці команди, але краще не експерементувати.__\n"
        )

        await event.reply(message)
