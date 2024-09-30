# modules/stealer.py

from service.bot import bot
from loguru import logger

from telethon import events
from telethon.tl.types import Channel, User

from modules.youtube import youtube_handler


def start_module():
    logger.info("Stealer module started")

    command = "!ssteal"

    async def get_username(message):
        username = (
            message.sender.title
            if type(message.sender) is Channel
            else (
                f"@{message.sender.username}"
                if type(message.sender) is User
                else message.sender.id
            )
        )
        return username

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern=command))
    async def stealer(event):
        if event.is_reply:

            target_msg = None
            input_str = event.message.message.replace(f"{command} ", "")
            reply_msg = await bot.get_messages(
                event.chat_id, ids=event.message.reply_to_msg_id
            )

            args = input_str.split()
            tags = [arg for arg in args if arg.startswith("#")]

            username = await get_username(reply_msg)

            caption = f"Вкрадено у {username}"

            is_raw_input = False
            is_album = False
            if "-q" in args and reply_msg.text != "":
                caption = f'Цитовано {username}:\n"{reply_msg.text}"'

            elif "-r" in args:
                is_raw_input = True
                caption = f'{input_str.replace("-r ", "")}'

            elif "-g" in args and reply_msg.grouped_id:
                is_album = True
                msg_list = await bot.get_messages(
                    reply_msg.chat_id,
                    limit=11,
                    min_id=int(reply_msg.id) - 11,
                    max_id=int(reply_msg.id) + 11,
                )

                if reply_msg.grouped_id:
                    target_msg = []
                    for msg in msg_list[::-1]:
                        if msg.grouped_id == reply_msg.grouped_id:
                            target_msg.append(msg)

            elif "-d" in args:
                if "-p" in args:
                    await youtube_handler(
                        reply_msg, post=True, external_args=args, external=True
                    )
                else:
                    await youtube_handler(
                        reply_msg, post=False, external_args=args, external=True
                    )
                return

            if not is_album:
                target_msg = reply_msg

            if not is_raw_input:
                if tags:
                    caption += "\n\n"
                    for tag in tags:
                        caption += f"{tag}\n"
                else:
                    caption += "\n\n#meme"

            try:
                await bot.send_message(bot.channel, file=target_msg, message=caption)

            except TypeError as e:
                logger.error(f"Type error: {e}")
                await event.reply(
                    f"__Ти що намагаєшся вкрасти, текст? Ну я хз короче, лови помилку:__\n`{e}`",
                )
