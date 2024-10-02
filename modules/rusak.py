import asyncio
from service.bot import bot
from loguru import logger


async def send_command_and_check_response(chat_id, command, success_msgs):
    # Відправляємо команду
    await bot.send_message(chat_id, command)

    # Отримуємо відповідь
    messages = await bot.get_messages(chat_id, limit=1)
    answer = messages[0]

    # Позначаємо повідомлення як прочитане
    await bot.send_read_acknowledge(chat_id, message=answer, clear_mentions=True)

    # Перевіряємо, чи містить повідомлення успішний текст
    return any(success_text in answer.text for success_text in success_msgs), answer


async def process_mine_chat(chat_id, count):
    for _ in range(count):
        success = False

        while not success:
            success, answer = await send_command_and_check_response(
                chat_id,
                "/mine",
                ["успішно відпрацював зміну", "сьогодні відпрацював зміну"],
            )

        await send_command_and_check_response(
            chat_id, "/swap", []
        )  # swap також через метод
        await asyncio.sleep(1)


async def process_rusak_bot(chat_id, count):
    await send_command_and_check_response(chat_id, "/woman", [])
    await asyncio.sleep(1)

    for _ in range(count):
        artefact, answer = await send_command_and_check_response(
            chat_id, "/i", ["Артефакт Серце Оази"]
        )

        while artefact:
            await answer.buttons[0][1].click()
            inventory = await bot.get_messages(chat_id, ids=answer.id)

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
                        await send_command_and_check_response(
                            chat_id, "Закінчився цукор, русак голодний", []
                        )

        success = False
        while not success:
            success, answer = await send_command_and_check_response(
                chat_id, "/feed", ["смачно поїв", "хватить з нього", "захворів"]
            )

        await send_command_and_check_response(chat_id, "/swap", [])
        await asyncio.sleep(1)


async def process_raid_chat(chat_id):
    await send_command_and_check_response(chat_id, "/raid", [])


mine_chat_id = 1211933154
rusak_bot_id = 6277866886
homosekus_chat_id = 1462197724
rusaks = 2


async def feed_work_and_mine():
    await process_mine_chat(mine_chat_id, rusaks)
    await process_rusak_bot(rusak_bot_id, rusaks)
    await send_command_and_check_response(homosekus_chat_id, "/work", [])


async def start_raid():
    await process_raid_chat(homosekus_chat_id)


def start_module():
    logger.info("Rusak module started")
