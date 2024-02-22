# modules/unpinner.py

import asyncio

from service.bot import bot
from loguru import logger

from telethon import events
from telethon.tl.custom.message import Message
from telethon.errors import FloodWaitError
from telethon.tl.types import InputMessagesFilterPinned, Channel, User


def start_module():
    logger.info("Unpinner module started")

    @bot.on(events.NewMessage(from_users=290522978, pattern="!unpin all"))
    async def unpin_all(event):
        any_pinned = True

        try:
            while any_pinned:
                pinned_messages = await bot.get_messages(
                    2078884005,
                    filter=InputMessagesFilterPinned,
                    limit=1000,
                )

                if pinned_messages:
                    try:
                        for msg in pinned_messages:
                            if type(msg.sender) is Channel:
                                await Message.unpin(msg)
                                logger.info(f"Message id:{msg.id} - unpinned")
                                await asyncio.sleep(15)
                            elif type(msg.sender) is User:
                                pass
                            else:
                                raise Exception

                    except FloodWaitError as flood_error:
                        logger.warning(flood_error)
                        await asyncio.sleep(flood_error.seconds)
                        logger.trace("Continue operations")
                        continue

                else:
                    logger.info("No pinned message!")
                    any_pinned = False

        except Exception as e:
            logger.error(f"Some errors here! {e}")

    @bot.on(events.NewMessage(chats=2078884005, from_users=2011709586))
    async def unpin_single(event):
        while True:
            try:
                if type(event.message.sender) is Channel:
                    await Message.unpin(event.message)
                    logger.info(f"Message id:{event.message.id} - unpinned")
                    await asyncio.sleep(60)
                    break
                elif type(event.message.sender) is User:
                    pass
                else:
                    raise Exception

            except FloodWaitError as flood_error:
                logger.warning(flood_error)
                await asyncio.sleep(flood_error.seconds)
                logger.trace("Continue operations")
                continue

            except Exception as e:
                logger.error(f"Some errors here! {e}")
