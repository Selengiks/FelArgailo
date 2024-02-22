# modules/stealer.py

from service.bot import bot
from loguru import logger

from telethon import events


def start_module():
    logger.info("Stealer module started")

    command = "!ssteal"

    @bot.on(events.NewMessage(from_users=bot.allowed_users, pattern=command))
    async def stealer(event):
        if event.is_reply:

            target_msg = event.message.message.replace(f"{command} ", "")
            reply_msg = await bot.get_messages(
                event.chat_id, ids=event.message.reply_to_msg_id
            )

            args = event.message.message.split()
            tags = [arg for arg in args if arg.startswith("#")]

            caption = f"Вкрадено у @{reply_msg.sender.username}"
            if "-q" in args and reply_msg.text != "":
                is_flag = True
                caption = f'Цитовано @{reply_msg.sender.username}: "{reply_msg.text}"'

            elif "-c" in args:
                is_flag = True
                caption = f'{target_msg.replace("-c ", "")}\n\nВкрадено у @{reply_msg.sender.username}'

            else:
                is_flag = False

            if not is_flag:
                if tags:
                    caption += "\n\n"
                    for tag in tags:
                        caption += f"{tag}\n"
                else:
                    caption += "\n\n#meme"

            target_msg = reply_msg
            target_msg.text = caption
            await bot.send_message(bot.channel, message=target_msg)
