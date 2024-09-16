# modules/pixiv.py

import re
import os
from pixivpy3 import AppPixivAPI
from telethon import events
from service.bot import bot
from loguru import logger


pixiv_api = AppPixivAPI()


def get_pixiv_artwork(artwork_id):
    try:
        pixiv_api.set_auth(
            access_token=bot.pixiv_access_token, refresh_token=bot.pixiv_refresh_token
        )
        pixiv_api.auth(refresh_token=bot.pixiv_refresh_token)

        json_result = pixiv_api.illust_detail(artwork_id)
        illust = json_result.illust
        if illust is None:
            logger.error(f"Illustration with ID {artwork_id} not found.")
            return None

        media_urls = []
        if illust.meta_single_page:
            media_urls.append(illust.meta_single_page.get("original_image_url"))

        elif illust.meta_pages:
            for page in illust.meta_pages:
                media_urls.append(page.image_urls.original)

        return media_urls

    except Exception as e:
        logger.error(f"Error during retrieving illustration from Pixiv: {e}")
        return None


def download_images(img_urls):
    pixiv_temp_dir = bot.temp_dir + "/pixiv/"
    media_files = []

    if not os.path.exists(pixiv_temp_dir):
        os.makedirs(pixiv_temp_dir)

    for img_url in img_urls:
        img_filename = img_url.split("/")[-1]
        img_path = os.path.join(pixiv_temp_dir, img_filename)
        pixiv_api.download(url=img_url, path=pixiv_temp_dir)

        media_files.append(img_path)

    return media_files


def parse_tags(message_text):
    tags = re.findall(r"#\w+", message_text)
    if not tags:
        tags = ["#art"]
    return tags


def start_module():
    logger.info("Pixiv module started")

    @bot.on(events.NewMessage(from_users=bot.allowed_users, chats=bot.service_chat_id))
    async def pixiv_handler(event):
        message_text = event.message.message

        pixiv_pattern = r"(https?://(?:www\.)?pixiv\.net/en/artworks/\d+)"
        pixiv_match = re.search(pixiv_pattern, message_text)

        if pixiv_match:
            message = await event.reply(f"🗿 Опа, піксівимо, ща глянемо що там...")

            pixiv_url = pixiv_match.group(1)
            artwork_id = re.search(r"/artworks/(\d+)", pixiv_url).group(1)

            try:
                img_urls = get_pixiv_artwork(artwork_id)

                if not img_urls:
                    await event.reply("Щось я нічого не знайшов, тож іди гуляй.")
                    return

                await bot.edit_message(
                    message, "Знайшов пост, ща вкрадем 👀"
                )

                media_files = download_images(img_urls)

                tags = parse_tags(message_text)
                caption = f"[Pixiv]({pixiv_url})\n\n" + "\n".join(tags)

                try:
                    await bot.send_message(
                        bot.channel, file=media_files, message=caption
                    )
                    await bot.edit_message(
                        message, "Во👍. Пост успішно вкрадено на канал"
                    )
                except Exception as e:
                    logger.error(f"Error post to channel: {e}")
                    await event.reply("Щось у мене нема настрою постити з Піксіву...")

            except Exception as e:
                logger.error(f"Error processing Pixiv: {e}")
                await event.reply("Щось пішло не так із крадіжкою з Піксіву...")
