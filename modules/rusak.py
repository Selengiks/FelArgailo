# modules/rusak.py

import asyncio
import aiocron
from service.bot import bot
from loguru import logger


async def send_command_and_check_response(conv, command, success_msgs):
    await conv.send_message(command)
    answer = await conv.get_response()

    return any(success_text in answer.text for success_text in success_msgs), answer


async def process_mine_chat(conv, count):

    for _ in range(count):
        success = False

        while not success:
            success, answer = await send_command_and_check_response(
                conv,
                "/mine",
                ["успішно відпрацював зміну", "сьогодні відпрацював зміну"],
            )

        await conv.send_message("/swap")
        await asyncio.sleep(1)


async def process_rusak_bot(conv, count):

    await conv.send_message("/woman")
    await asyncio.sleep(1)

    for _ in range(count):
        artefact, answer = await send_command_and_check_response(
            conv, "/i", ["Артефакт Серце Оази"]
        )

        while artefact:
            await answer.buttons[0][1].click()
            inventory = await bot.get_messages(conv.chat_id, ids=answer.id)
            nested = True
            for button in inventory.buttons:
                while nested:
                    for nested_button in button:
                        if "Цукор" in nested_button.text:
                            await nested_button.click()
                            artefact = False
                            nested = False
                            break
                    else:
                        await conv.send_message("Закінчився цукор, русак голодний")

        success = False
        while not success:
            success, answer = await send_command_and_check_response(
                conv, "/feed", ["смачно поїв", "хватить з нього", "захворів"]
            )

        await conv.send_message("/swap")
        await asyncio.sleep(1)


async def aiocron_func():
    mine_chat_id = 1211933154
    rusak_bot_id = 6277866886
    rusaks = 2

    async with bot.conversation(mine_chat_id) as mine_conv:
        await process_mine_chat(mine_conv, rusaks)

    async with bot.conversation(rusak_bot_id, exclusive=False) as rusak_conv:
        await process_rusak_bot(rusak_conv, rusaks)


async def start_daily_tasks():
    @aiocron.crontab("0 1 * * *")
    async def daily_tasks():
        await aiocron_func()


def start_module():
    logger.info("Rusak module started")
    asyncio.ensure_future(start_daily_tasks())
