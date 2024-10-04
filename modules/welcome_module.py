# modules/welcome_module.py

from telethon import events
from service.bot import bot
from service.plugins_manager import PluginManager
from loguru import logger


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
            f"`{', '.join(successful_modules) if num_successful_modules else 'Немає підключених модулів'}`\n\n"
            "**Вимкнені модулі:**\n"
            f"`{', '.join(disabled_modules) if num_disabled_modules else 'Немає вимкнених модулів'}`\n\n"
            "**Проблемні модулі:**\n"
            f"`{', '.join(f'{module} ({error})' for module, error in problematic_modules) if num_problematic_modules else 'Немає проблемних модулів'}`\n\n"
        )

        await event.reply(message)

    @bot.on(events.NewMessage(pattern="!hhelp"))
    async def felix_help(event):
        message = (
            "**Кібер-Фелікс**:\n"
            "**Stealer** - __щоб вкрасти мем, чи арт, введи команду `!ssteal` у відповідь "
            "на медіа, яке хочеш вкрасти. За замовчуванням, ставиться тег #meme. Для керування, наявні прапори:__\n"
            "    `-q` - __краде медіа із оригінальним підписом, і кидає як цитату.__\n"
            '    `-r` "текст"- __краде медіа з текстом, який слідує після команди.__ \n'
            "    `-g` - __дозволяє вкрасти множину медіа (якщо користувач скинув групу медіа).__\n"
            "    `-d` - __дозволяє завантажити меді з Ютубу, якщо посилання на нього буде у повідомленні.__\n"
            "    **Після прапора -d, Доступні опціональні прапори вибору якості:**\n"
            "    `-p` - __постить дане відео на канал [ЛИШЕ ДЛЯ АДМІНІВ КАНАЛУ]__\n"
            "    `-lq` - __Low quality, буде завантажувати відео з порогом якості в 480p__\n"
            "    `-mq` - __Medium quality (за замовчуванням), буде завантажувати відео з порогом якості в 720p__\n"
            "    `-hq` - __High quality, буде завантажувати відео з порогом якості в 1080p__\n"
            "    `-bq` - __Best quality, буде завантажувати відео з максимально доступною якістю__\n"
            "    `-ea` - __Extract audio, прапор дозволяє завантажити та витягнути аудіо__\n\n"
            "**Примітка**:\n"
            "    -__Щоб вкрасти медіа з дефолтним підписом, але іншим тегом, введи `!ssteal #tag`.__\n"
            "    -__Можна ввести множину тегів, наприклад `!ssteal #tag1 tag2`.__\n"
            "    -__Пожалійте сервер і Фелікса, не зловживайте закачкою відосів у макc. якості.__\n"
        )

        await event.reply(message)
