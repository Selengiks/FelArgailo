# modules/moderator.py

from service.bot import bot
from loguru import logger

from telethon import events


def start_module():
    logger.info("Moderator module started")

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern="!warn"))
    async def warn_user(event):
        if event.is_reply:
            pass

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern="!mute"))
    async def mute_user(event):
        if event.is_reply:
            pass

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern="!ban"))
    async def ban_user(event):
        if event.is_reply:
            pass

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern="!kick"))
    async def kick_user(event):
        if event.is_reply:
            pass

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern="!bot"))
    async def ban_bot(event):
        if event.is_reply:
            pass
