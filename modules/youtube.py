import time
import os
import re
from yt_dlp import YoutubeDL
from telethon import events
from service.bot import bot
from loguru import logger


# Форматування розміру файлу
def format_size(size):
    for unit in ["Б", "КБ", "МБ"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


# Отримання якості відео з повідомлення
def get_media_quality(message_text):
    quality_map = {"-lq": 480, "-mq": 720, "-hq": 1080, "-bq": "BQ", "-ea": "audio"}
    for key, value in quality_map.items():
        if key in message_text:
            return value
    return 720  # За замовчуванням


# Оновлення прогресу завантаження
async def callback(current, total, message):
    if not hasattr(callback, "last_update_time"):
        callback.last_update_time = 0
    if not hasattr(callback, "update_interval"):
        callback.update_interval = 5

    percentage = (current / total) * 100
    current_time = time.time()

    # Оновлюємо повідомлення кожні 5 секунд
    if current_time - callback.last_update_time > callback.update_interval:
        current_mb, total_mb = current / (1024**2), total / (1024**2)
        callback_msg = (
            f"{percentage:.2f}% Uploaded: {current_mb:.2f} MB out of {total_mb:.2f} MB"
        )
        logger.trace(callback_msg)
        await bot.edit_message(message, callback_msg)
        callback.last_update_time = current_time


# Завантаження відео з YouTube
def download_youtube_media(video_url, quality):
    youtube_temp_dir = os.path.join(bot.temp_dir, "youtube")
    os.makedirs(youtube_temp_dir, exist_ok=True)

    if quality == "audio":  # Якщо аудіо, використовуємо bestaudio
        media_format = "bestaudio/best"
        output_format = "mp3"
        ydl_opts = {
            "cookiesfrombrowser": ("firefox",),
            "format": media_format,
            "outtmpl": os.path.join(youtube_temp_dir, f"%(title)s_{quality}.%(ext)s"),
            "postprocessors": [
                {  # Додаємо конвертацію в mp3
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
        }
    else:  # Інакше завантажуємо відео
        media_format = (
            f"bestvideo[height<={quality}]+bestaudio/best"
            if isinstance(quality, int)
            else "best"
        )
        output_format = "mp4"
        ydl_opts = {
            "cookiesfrombrowser": ("firefox",),
            "format": media_format,
            "outtmpl": os.path.join(youtube_temp_dir, f"%(title)s_{quality}.%(ext)s"),
            "merge_output_format": output_format,
            "quiet": True,
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            media_path = (
                os.path.splitext(ydl.prepare_filename(info_dict))[0]
                + f".{output_format}"
            )
        return media_path
    except Exception as e:
        logger.error(f"Error downloading media from YouTube: {e}")
        return None


# Парсинг тегів з повідомлення
def parse_tags(message_text, is_audio=False):
    if is_audio:
        return ["#music"]

    tags = re.findall(r"#\w+", message_text)
    return tags if tags else ["#meme"]


# Основний обробник YouTube-повідомлень
async def youtube_handler(event, external=False, sender_type=None):
    msg = (
        event.message
        if not external
        else await bot.get_messages(event.chat_id, ids=event.message.reply_to_msg_id)
    )

    post = (
        True
        if "-p" in msg.message.join(event.message.message.split(" "))
        and sender_type == "superadmin"
        else False
    )

    youtube_url_match = re.search(
        r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w-]+)",
        str(msg.message),
    )
    if youtube_url_match:
        youtube_url = youtube_url_match.group(1)
        message = await event.reply("🗿 Опа, ютубчик, ща вкрадемо...")

        try:
            quality = get_media_quality(event.message.message)
            video_path = download_youtube_media(youtube_url, quality)

            if not video_path:
                logger.warning("No media found")
                await event.reply("Щось я нічого не знайшов, тож іди гуляй")
                return

            await bot.edit_message(message, "Скачав медіа, ща завантажимо 👀")
            tags = parse_tags(
                msg.message + " " + event.message.message,
                is_audio=True if quality == "audio" else False,
            )

            total_size = os.path.getsize(video_path)
            caption = f"[Соурс]({youtube_url})"

            if post:
                caption += "\n\n" + "\n".join(tags)
                await bot.send_file(
                    bot.channel,
                    caption=caption,
                    file=video_path,
                    progress_callback=lambda c, t: callback(c, t, message),
                    supports_streaming=not quality == "audio",
                )
                await bot.edit_message(
                    message,
                    f"Во👍. Медіа успішно вкрадено на канал\n\nЗавантажено файл розміром {format_size(total_size)}",
                )
            else:
                await bot.send_file(
                    event.chat_id,
                    caption=caption
                    + f"\n\nВо👍. Завантажено медіа розміром {format_size(total_size)}",
                    file=video_path,
                    progress_callback=lambda c, t: callback(c, t, message),
                    supports_streaming=not quality == "audio",
                )

                await bot.delete_messages(
                    msg.chat,
                    message_ids=(
                        [message.id, msg.id]
                        if not external
                        else (
                            [message.id, event.message.id]
                            if msg.sender_id != event.sender_id
                            else [message.id, event.message.id, msg.id]
                        )
                    ),
                )

        except Exception as e:
            logger.error(f"Error processing YouTube media: {e}")
            await bot.edit_message(
                message, f"Сталася помилка при завантажуванні медіа: {e}"
            )


# Запуск модуля
def start_module():
    logger.info("YouTube module started")

    @bot.on(events.NewMessage(from_users=bot.allowed_users, chats=bot.service_chat_id))
    async def handle_youtube_handler(event):
        await youtube_handler(event, sender_type="superadmin")
