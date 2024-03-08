# modules/waifu_catcher.py

import asyncio
import aiocron
from service.bot import bot
from telethon import events
from loguru import logger


async def start_daily_tasks():
    @aiocron.crontab("0 1 * * *")
    @bot.on(events.NewMessage(chats=1259755561, pattern="!waifu"))
    async def daily_tasks(event):
        waifu_catcher_id = 1976201765

        async with bot.conversation(waifu_catcher_id, exclusive=False) as catcher_conv:
            await catcher_conv.send_message("/start")

            @bot.on(events.NewMessage(chats=waifu_catcher_id))
            async def handle_bot_messages(bot_message_event):
                test = bot_message_event
                print(test)


def start_module():
    logger.info("Waifu catcher module started")
    asyncio.ensure_future(start_daily_tasks())
