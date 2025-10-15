from service.bot import bot
from telethon.tl.types import (
    Channel,
    User,
    PeerUser,
    PeerChannel,
)
from telethon.errors.rpcerrorlist import ChannelPrivateError


async def get_username(message, original_poster: bool = False):
    if not original_poster:
        return (
            f"@{message.sender.username}"
            if message.sender.username
            else (
                message.sender.first_name
                if message.sender.first_name
                else message.sender.id
            )
        )

    if message.fwd_from:
        if isinstance(message.fwd_from.from_id, PeerUser):
            user_entity = await bot.get_entity(message.fwd_from.from_id.user_id)
            username = (
                f"@{user_entity.username}"
                if user_entity.username
                else (
                    user_entity.first_name if user_entity.first_name else user_entity.id
                )
            )
        elif isinstance(message.fwd_from.from_id, PeerChannel):
            try:
                channel_entity = await bot.get_entity(
                    message.fwd_from.from_id.channel_id
                )
                username = (
                    f"@{channel_entity.username}"
                    if channel_entity.username
                    else (
                        channel_entity.title
                        if channel_entity.title
                        else channel_entity.id
                    )
                )
            except ChannelPrivateError:
                username = (
                    f"@{message.sender.username}"
                    if message.sender.username
                    else (
                        message.sender.first_name
                        if message.sender.first_name
                        else message.sender.id
                    )
                )
        else:
            username = None
    else:
        if isinstance(message.sender, Channel):
            username = (
                f"@{message.sender.username}"
                if message.sender.username
                else (
                    message.sender.title if message.sender.title else message.sender.id
                )
            )
        elif isinstance(message.sender, User):
            username = (
                f"@{message.sender.username}"
                if message.sender.username
                else (
                    message.sender.first_name
                    if message.sender.first_name
                    else message.sender.id
                )
            )
        else:
            username = None
            logger.error(f"Unknown sender type: {type(message.sender)}")

    return username
