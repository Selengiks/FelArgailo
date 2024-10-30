# modules/test_env.py

import asyncio
import aiocron
from service.bot import bot
from telethon import events
from loguru import logger


def start_module():
    logger.info("Test environment started")

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern="!ttest"))
    async def test(event):
        pass
