# modules/waifu_catcher.py

import asyncio
import aiocron
from service.bot import bot
from loguru import logger


async def aiocron_func():
    pass


async def start_daily_tasks():
    @aiocron.crontab("0 1 * * *")
    async def daily_tasks():
        await aiocron_func()


def start_module():
    logger.info("Waifu catcher module started")
    asyncio.ensure_future(start_daily_tasks())
