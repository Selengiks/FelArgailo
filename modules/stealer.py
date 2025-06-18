import time

from telethon.helpers import TotalList

from service.bot import bot
from loguru import logger

from telethon import events
from telethon.tl.types import Channel, User, ChannelParticipantsAdmins, PeerUser, PeerChannel

try:
    from modules.youtube import youtube_handler

    youtube_module = True
except ImportError:
    youtube_module = False
    logger.warning("Youtube module is not installed")


def start_module():
    logger.info("Stealer module started")

    command = "!ssteal"

    async def get_username(message):
        if message.fwd_from:
            if isinstance(message.fwd_from.from_id, PeerUser):
                user_entity = await bot.get_entity(message.fwd_from.from_id.user_id)
                username = f"@{user_entity.username}" if user_entity.username else user_entity.first_name if user_entity.first_name else user_entity.id
            elif isinstance(message.fwd_from.from_id, PeerChannel):
                channel_entity = await bot.get_entity(message.fwd_from.from_id.channel_id)
                username = f"@{channel_entity.username}" if channel_entity.username else channel_entity.title if channel_entity.title else channel_entity.id
            else:
                username = None
        else:
            if isinstance(message.sender, Channel):
                username = f"@{message.sender.username}" if message.sender.username else message.sender.title if message.sender.title else message.sender.id
            elif isinstance(message.sender, User):
                username = f"@{message.sender.username}" if message.sender.username else message.sender.first_name if message.sender.first_name else message.sender.id
            else:
                username = None
                logger.error(f"Unknown sender type: {type(message.sender)}")

        return username

    async def get_sender_role(event):
        superadmins = bot.allowed_users
        admins = [
            user.id
            async for user in bot.iter_participants(
                event.chat_id, filter=ChannelParticipantsAdmins
            )
        ]

        sender_id = event.message.sender_id

        if sender_id in superadmins:
            return "superadmin"
        elif sender_id in admins:
            return "admin"
        else:
            return "user"

    @bot.on(events.NewMessage(pattern=command))
    async def stealer(event):
        sender_role = await get_sender_role(event)

        if sender_role == "user":
            # Якщо юзер — просто ігноруємо
            return

        # Якщо є відповідь на повідомлення
        if event.is_reply:
            input_str = event.message.message.replace(f"{command} ", "")
            reply_msg = await bot.get_messages(event.chat_id, ids=event.reply_to_msg_id)
            args = input_str.split()
            tags = [arg for arg in args if arg.startswith("#")]

            username = await get_username(reply_msg)
            if username:
                caption = f"Вкрадено у {username}"
            else:
                caption = ""
            is_raw_input = False
            is_album = False
            target_msg = None

            # Для суперадмінів — весь функціонал
            if sender_role == "superadmin":
                # Суперадмін може все, що й адмін
                if youtube_module:
                    if "-d" in args:
                        await youtube_handler(
                            event, external=True, sender_type=sender_role
                        )
                        return
                if "-q" in args and reply_msg.text:
                    caption = f'Цитовано {username}:\n"{reply_msg.text}"'
                elif "-r" in args:
                    is_raw_input = True
                    caption = input_str.replace("-r ", "")
                elif (
                    "-g" in args and reply_msg.grouped_id
                ):  # TODO: додати сумісність -g прапору з іншими
                    is_album = True
                    msg_list = await bot.get_messages(
                        reply_msg.chat_id,
                        limit=11,
                        min_id=int(reply_msg.id) - 11,
                        max_id=int(reply_msg.id) + 11,
                    )
                    target_msg = [
                        msg
                        for msg in msg_list[::-1]
                        if msg.grouped_id == reply_msg.grouped_id
                    ]
                if not is_album:
                    target_msg = reply_msg

                # Додаємо теги або #meme, якщо теги відсутні
                if not is_raw_input:
                    caption += "\n\n" + "\n".join(tags) if tags else ("#meme" if not caption else "\n\n#meme")

            # Для адмінів — також дозволити команду з -d
            elif sender_role == "admin":
                if youtube_module:
                    if "-d" in args:
                        await youtube_handler(
                            event, external=True, sender_type=sender_role
                        )
                        return
                    else:
                        await event.reply("⛔️ Доступна лише команда з прапором -d")
                        return

            # Відправка повідомлення в канал
            try:
                if target_msg:
                    await bot.send_message(
                        bot.channel, file=target_msg, message=caption
                    )
                time.sleep(5)
                await bot.delete_messages(event.chat_id, message_ids=event.message.id)
            except TypeError as e:
                logger.error(f"Type error: {e}")
                await event.reply(
                    f"__Ти що намагаєшся вкрасти, текст? Ну я хз короче, лови помилку:__\n`{e}`",
                )
