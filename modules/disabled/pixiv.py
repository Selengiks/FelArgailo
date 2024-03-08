# modules/pixiv.py

from service.bot import bot
from loguru import logger

from telethon import events


def start_module():
    logger.info("Pixiv module started")

    @bot.on(events.NewMessage(chats=bot.channel, pattern="((https|http):\/\/.*)"))
    async def format_pixiv_url(event):
        test = event
        print(test)
