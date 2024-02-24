# modules/rusak.py

import asyncio
import aiocron
from service.bot import bot
from loguru import logger


async def send_command_and_check_response(conv, command, success_msgs):
    await conv.send_message(command)
    answer = await conv.get_response()
    return any(success_text in answer.text for success_text in success_msgs), answer


async def process_mine_chat(conv, counter):
    success, answer = await send_command_and_check_response(conv, "/mine", ['сьогодні відпрацював зміну',
                                                                            'успішно відпрацював зміну'])
    if success:
        await conv.send_message("/swap")
        counter += 1

    return counter


async def process_rusak_bot(conv, counter):
    async def send_and_check(command, success_msgs):
        return await send_command_and_check_response(conv, command, success_msgs)

    await conv.send_message("/woman")
    await asyncio.sleep(1)
    for _ in range(2):
        success, answer = await send_and_check("/i", ["Артефакт Серце Оази"])
        if success:
            await answer.buttons[0][1].click()
            inventory = await bot.get_messages(conv.chat_id, ids=answer.id)
            for button in inventory.buttons:
                for nested_button in button:
                    if "Цукор" in nested_button.text:
                        await nested_button.click()
                        break
                else:
                    await conv.send_message("Закінчився цукор, русак голодний")

        success, answer = await send_and_check("/feed", ["смачно поїв", "хватить з нього", "захворів"])
        if success:
            await conv.send_message("/swap")
            counter += 1

        if counter == 2:
            break

    return counter


async def aiocron_func():
    mine_chat_id = 1211933154
    rusak_bot_id = 6277866886

    async with bot.conversation(mine_chat_id) as mine_conv:
        counter = 0
        while counter < 2:
            counter = await process_mine_chat(mine_conv, counter)

    async with bot.conversation(rusak_bot_id, exclusive=False) as rusak_conv:
        counter = 0
        while counter < 2:
            counter = await process_rusak_bot(rusak_conv, counter)


async def start_daily_tasks():
    @aiocron.crontab("0 1 * * *")
    async def daily_tasks():
        await aiocron_func()


def start_module():
    logger.info("Rusak module started")
    asyncio.ensure_future(start_daily_tasks())
