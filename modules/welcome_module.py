# modules/welcome_module.py

from telethon import events
from service.bot import bot
from loguru import logger


def start_module():
    logger.info("Welcome module started")

    @bot.on(events.NewMessage(pattern="/felix_argyle"))
    async def send_welcome(event):
        await event.reply("Howdy, how are you doing?")
