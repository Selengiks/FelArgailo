# service/scheduler.py

import aiocron
import asyncio
from loguru import logger
from modules.rusak import feed_work_and_mine, start_raid
from service.temp_files_remover import cleanup_temp_files


async def aiocron_scheduler():

    @aiocron.crontab("0 */6 * * *")  # Кожні 6 годин
    async def process_cleanup():
        await cleanup_temp_files()

    @aiocron.crontab("0 1 * * *")  # Щодня о 01:00
    async def process_rusak_daily():
        await feed_work_and_mine()

    # @aiocron.crontab("0 8-23 * * *")  # Щогодини з 8 до 23
    # async def process_raid_start():
    #     await start_raid()


def start_scheduler():
    logger.info("Aiocron scheduler started")
    asyncio.ensure_future(aiocron_scheduler())
