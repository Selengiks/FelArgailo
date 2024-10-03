# main_bot.py

from service.bot import bot
from service.logger import start_logger
from service.plugins_manager import PluginManager
from service.scheduler import start_scheduler
from telethon.errors import FloodWaitError
import asyncio
from loguru import logger


async def run_bot():
    while True:
        try:
            start_logger("DEBUG")
            PluginManager.load_modules()
            start_scheduler()

            async with bot:
                await bot.run_until_disconnected()
        except FloodWaitError as e:
            logger.warning(
                f"Received FloodWait! Wait {e.seconds} seconds to continue..."
            )
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.warning(f"Error: {e}. Restart after 60 seconds...")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(run_bot())
