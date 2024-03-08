# modules/wip_container.py

import asyncio
import aiocron
from service.bot import bot
from telethon import events
from loguru import logger


def start_module():
    logger.info("WIP module started")
