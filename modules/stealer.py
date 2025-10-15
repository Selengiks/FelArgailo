import time
from service.bot import bot
from loguru import logger
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins
from service.help_manager import HelpManager
from utils.utils import get_username

try:
    from modules.youtube import youtube_handler

    youtube_module = True
except ImportError:
    youtube_module = False
    logger.warning("Youtube module is not installed")


class MediaFlag:
    def __init__(self, flag: str, tag: str = None, superadmin_only: bool = False):
        self.flag = flag
        self.tag = tag
        self.superadmin_only = superadmin_only


class MediaFlags:
    FLAGS = {
        "raw": MediaFlag("-r"),  # Сирий текст без модифікацій
        "source": MediaFlag("-s"),  # Показувати оригінального автора
        "quote": MediaFlag("-q"),  # Цитування тексту
        "gallery": MediaFlag("-g"),  # Альбом/галерея
        "art": MediaFlag("-a", "#art"),  # Арт
        "cunny": MediaFlag("-c", "#cunny"),  # Канні
        "download": MediaFlag("-d"),  # Завантаження медіа
    }

    def __init__(self, args: list):
        self.flags = []
        self.tags = []

        for arg in args:
            for flag in self.FLAGS.values():
                if arg == flag.flag:
                    self.flags.append(flag)
                    if flag.tag:
                        self.tags.append(flag.tag)
            if arg.startswith("#"):
                self.tags.append(arg)

    def has_flag(self, flag_name: str) -> bool:
        return any(f.flag == self.FLAGS[flag_name].flag for f in self.flags)

    def get_tags(self) -> str:
        return "\n\n" + "\n".join(self.tags) if self.tags else ""

    def is_raw(self) -> bool:
        return self.has_flag("raw")

    def show_source(self) -> bool:
        return not self.has_flag("source")

    def is_gallery(self) -> bool:
        return self.has_flag("gallery")

    def is_quote(self) -> bool:
        return self.has_flag("quote")

    def is_download(self) -> bool:
        return self.has_flag("download")


def get_help_text():
    return (
        "**Stealer** - __щоб вкрасти мем, чи арт, введи команду `!ssteal` у відповідь "
        "на медіа, яке хочеш вкрасти. За замовчуванням, ставиться тег #meme. Для керування, наявні прапори:__\n"
        "    `-q` - __краде медіа із оригінальним підписом, і кидає як цитату.__\n"
        '    `-r` "текст"- __краде медіа з текстом, який слідує після команди.__ \n'
        "    `-g` - __дозволяє вкрасти множину медіа (якщо користувач скинув групу медіа).__\n"
        "    `-s` - __приховує джерело медіа.__\n"
        "    `-a` - __додає тег #art.__\n"
        "    `-c` - __додає тег #cunny.__\n"
        "    `-d` - __дозволяє завантажити медіа з Ютубу.__\n"
    )


def start_module():
    logger.info("Stealer module started")
    HelpManager.register_help("stealer", get_help_text())
    command = "!ssteal"

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

    async def process_media_message(event, reply_msg, flags: MediaFlags, sender_role):
        if sender_role == "user":
            return None

        # Для адмінів дозволяємо тільки завантаження
        if sender_role == "admin":
            if youtube_module and flags.is_download():
                await youtube_handler(
                    event, external=True, sender_type=sender_role, mode="command"
                )
            else:
                await event.reply("⛔️ Доступна лише команда з прапором -d")
            return None

        # YouTube обробка для суперадмінів
        if youtube_module and flags.is_download():
            await youtube_handler(
                event, external=True, sender_type=sender_role, mode="command"
            )
            return None

        input_str = event.message.message.replace(f"{command} ", "")
        username = await get_username(reply_msg, flags.show_source())
        caption = f"Вкрадено у {username}" if username else ""
        target_msg = None
        is_album = False

        # Обробка прапорів
        if flags.is_quote() and reply_msg.text:
            caption = f'Цитовано {username}:\n"{reply_msg.text}"'
        elif flags.is_raw():
            caption = input_str
            for flag in MediaFlags.FLAGS.values():
                caption = caption.replace(flag.flag, "").strip()
        elif flags.is_gallery() and reply_msg.grouped_id:
            is_album = True
            limit = 11
            msg_list = await bot.get_messages(
                reply_msg.chat_id,
                limit=25,
                min_id=int(reply_msg.id) - limit,
                max_id=int(reply_msg.id) + limit,
                reverse=True,
            )
            target_msg = [
                msg for msg in msg_list if msg.grouped_id == reply_msg.grouped_id
            ]

        if not is_album:
            target_msg = reply_msg

        # Додавання тегів
        if not flags.is_raw():
            if caption:
                caption += flags.get_tags() or "\n\n#meme"
            else:
                caption += flags.get_tags()

        return target_msg, caption, is_album

    @bot.on(events.NewMessage(pattern=command))
    async def stealer(event):
        if not event.is_reply:
            return

        sender_role = await get_sender_role(event)
        args = event.message.message.replace(f"{command} ", "").split()
        flags = MediaFlags(args)
        reply_msg = await bot.get_messages(event.chat_id, ids=event.reply_to_msg_id)

        result = await process_media_message(event, reply_msg, flags, sender_role)
        if not result:
            return

        target_msg, caption, is_album = result

        try:
            if target_msg:
                await bot.send_message(bot.channel, file=target_msg, message=caption)
            time.sleep(3)
            await bot.delete_messages(event.chat_id, message_ids=event.message.id)
        except TypeError as e:
            logger.error(f"Type error: {e}")
            await event.reply(
                f"__Ти що намагаєшся вкрасти, текст? Ну я хз короче, лови помилку:__\n`{e}`"
            )
