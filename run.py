# main_bot.py

from service.bot import bot
from service.logger import setup_logger
from service.plugins_manager import PluginManager
from service.help_manager import HelpManager
from service.scheduler import start_scheduler
from telethon.errors import FloodWaitError
import asyncio
from loguru import logger


async def run_bot():
    while True:
        try:
            setup_logger()
            PluginManager.load_modules()
            [
                HelpManager.register_help(n, m.get_help_text())
                for n, m in PluginManager.get_successful_modules().items()
                if callable(getattr(m, "get_help_text", None))
            ]
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
    loop = asyncio.get_event_loop()
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt as SIGINT:
        logger.info("Caught keyboard interrupt. Canceling tasks...")

    finally:
        loop.close()
