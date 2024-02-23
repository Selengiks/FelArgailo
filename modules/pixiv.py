# modules/pixiv.py

from service.bot import bot
from loguru import logger

from telethon import events


def start_module():
    logger.info("Pixiv module started")

    @bot.on()
    async def format_pixiv_url(event):
        pass
