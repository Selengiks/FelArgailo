# modules/test_env.py

import asyncio
import aiocron
import spotdl
from service.bot import bot
from telethon import events
from loguru import logger


def start_module():
    logger.info("Test environment started")

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern="!ttest"))
    async def test(event):
        spot = spotdl.Spotdl
        input_str = event.message.message.replace(f"!ttest", "")
        result = spot.search(spot, query=[input_str])
        await bot.send_file(event.chat_id, file=result)
