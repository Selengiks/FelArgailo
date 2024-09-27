# modules/youtube.py

import time
import os
import re
from yt_dlp import YoutubeDL
from telethon import events
from service.bot import bot
from loguru import logger


# Форматування розміру
def format_size(size):
    """Конвертує розмір файлу в зручний формат з одиницями (Б, КБ, МБ, ГБ).

    Args:
        size (int): Розмір файлу в байтах.

    Returns:
        str: Розмір файлу у форматі з одиницями.
    """
    for unit in ["Б", "КБ", "МБ", "ГБ"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


# Отримання якості відео
def get_video_quality(message_text):
    """Визначає якість відео на основі параметрів у тексті повідомлення.

    Args:
        message_text (str): Текст повідомлення, що містить параметри якості.

    Returns:
        str: Формат для завантаження відео.
    """
    if "-lq" in message_text:
        return 480
    elif "-mq" in message_text:
        return 720
    elif "-hq" in message_text:
        return 1080
    elif "-bq" in message_text:
        return None


async def callback(current, total, message):
    """Оновлює повідомлення з прогресом завантаження відео.

    Args:
        current (int): Кількість завантажених байтів.
        total (int): Загальна кількість байтів для завантаження.
        message (Message): Повідомлення для оновлення.
    """
    # Використовуйте замикання, щоб зберегти стан між викликами
    if not hasattr(callback, "last_update_time"):
        callback.last_update_time = 0
    if not hasattr(callback, "update_interval"):
        callback.update_interval = 3  # Оновлювати кожні 3 секунди

    current_kb = current / 1024
    total_kb = total / 1024
    current_mb = current_kb / 1024
    total_mb = total_kb / 1024

    # Обчислюємо відсоток завершення
    percentage = (current / total) * 100

    # Перевіряємо, чи потрібно оновити повідомлення
    current_time = time.time()
    if current_time - callback.last_update_time > callback.update_interval:
        if total_mb >= 1:
            callback_msg = f"{percentage}% Uploaded: {current_mb:.2f} MB out of {total_mb:.2f} MB"
        else:
            callback_msg = f"{percentage}% Uploaded: {current_kb:.2f} KB out of {total_kb:.2f} KB"

        logger.trace(callback_msg)
        await bot.edit_message(message, callback_msg)

        # Оновлюємо значення часу
        callback.last_update_time = current_time


def download_youtube_video(video_url, quality):
    """Завантажує відео з YouTube за вказаним URL та якістю.

    Args:
        video_url (str): URL відео на YouTube.
        quality (str): Формат для завантаження відео.

    Returns:
        str: Шлях до завантаженого відео або None у разі помилки.
    """
    youtube_temp_dir = os.path.join(bot.temp_dir, "youtube")
    if not os.path.exists(youtube_temp_dir):
        os.makedirs(youtube_temp_dir)

    video_format = "bestvideo{q}+bestaudio/best".format(q=f"[height<={quality}]" if quality else "")

    ydl_opts = {
        "format": video_format,
        "outtmpl": os.path.join(youtube_temp_dir, f"%(title)s_{quality}.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
            video_path = os.path.splitext(video_filename)[0] + ".mp4"
        return video_path

    except Exception as e:
        error_message = f"Error downloading video from YouTube: {e}"
        logger.error(error_message)
        return None


def parse_tags(message_text):
    """Парсить теги з тексту повідомлення.

    Args:
        message_text (str): Текст повідомлення.

    Returns:
        list: Список тегів.
    """
    tags = re.findall(r"#\w+", message_text)
    if not tags:
        tags = ["#meme"]
    return tags


async def youtube_handler(event, external=False, external_args=None):
    """Обробляє нові повідомлення, що містять URL-адреси YouTube, і завантажує відео.

    Args:
        :param external_args: Список прапорів, що були передані із зовнішньої команди
        :param event: (NewMessage): Подія нового повідомлення.
        :param external: Прапор, чи викликаний був метод ззовні (з іншого модуля або що)
    """
    if not external:
        message_text = str(event.message.message)
    else:
        message_text = str(event.message) + " ".join(external_args)

    youtube_pattern = r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]+))"
    youtube_match = re.search(youtube_pattern, message_text)

    if youtube_match:
        message = await event.reply("🗿 Опа, ютубимо, ща вкрадемо відео...")
        youtube_url = youtube_match.group(1)

        # Отримуємо якість відео з параметрів
        video_quality = get_video_quality(message_text)

        try:
            video_path = download_youtube_video(youtube_url, video_quality)

            if not video_path:
                await event.reply("Щось я нічого не знайшов, тож іди гуляй")
                return

            await bot.edit_message(message, "Знайшов відео, ща вкрадемо 👀")

            tags = parse_tags(message_text)
            caption = f"[Соурс]({youtube_url})\n\n" + "\n".join(tags)

            try:
                total_size = os.path.getsize(video_path)

                # Відправка відео з оновленнями прогресу
                if not external:
                    target = bot.service_chat_id
                else:
                    target = event.chat.id

                await bot.send_file(
                    target,
                    caption=caption,
                    file=video_path,
                    progress_callback=lambda current, total: callback(
                        current, total, message
                    ),
                    supports_streaming=True,
                )

                await bot.edit_message(
                    message,
                    f"Во👍. Відео успішно вкрадено на канал\n\nЗавантажено відео розміром {format_size(total_size)}",
                )

            except Exception as e:
                logger.error(f"Error posting to channel: {e}")
                await event.reply(
                    f"Щось у мене нема настрою постити відео з YouTube... Можливо це через наступну хуйню: {e}"
                )

        except Exception as e:
            error_message = f"Сталася помилка при скачуванні відео: {e}"
            logger.error(error_message)
            await bot.edit_message(
                message, error_message
            )  # Надсилаємо повідомлення про помилку


def start_module():
    """Запускає модуль YouTube, який слухає нові повідомлення."""
    logger.info("YouTube module started")

    @bot.on(events.NewMessage(from_users=bot.allowed_users, chats=bot.service_chat_id))
    async def handle_youtube_handler(event):
        await youtube_handler(event)
