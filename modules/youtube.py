import time
import os
import re
import asyncio
from telethon import events
from service.bot import bot
from loguru import logger
from utils.utils import get_username
from service.help_manager import HelpManager


# Форматування розміру файлу
def format_size(size):
    for unit in ["Б", "КБ", "МБ"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


# Отримання якості відео з повідомлення
def get_media_quality(message_text):
    quality_map = {
        "-lq": 480,
        "-mq": 720,
        "-hq": 1080,
        "2k": 1440,
        "4k": 2160,
        "-bq": "best",
        "-ba": "audio",
        "-ea": "mp3",
    }
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
        callback_msg = f"{percentage:.2f}% Завантажено: {format_size(current)} / {format_size(total)}"
        logger.trace(callback_msg)
        await bot.edit_message(message, callback_msg)
        callback.last_update_time = current_time


async def download_youtube_media(video_url, quality, max_retries=3, retry_delay=5):
    youtube_temp_dir = os.path.join(bot.temp_dir, "youtube")
    os.makedirs(youtube_temp_dir, exist_ok=True)

    for attempt in range(max_retries):
        try:
            # Отримання ID медіа
            info_cmd = [
                bot.yt_dlp_path,
                "--no-playlist",
                "--print",
                "%(id)s",
                "--cookies",
                "cookies.txt",
                "--no-download",
                video_url,
            ]

            process = await asyncio.create_subprocess_exec(
                *info_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Помилка отримання ID медіа: {stderr.decode()}")

            video_id = stdout.decode().strip()
            logger.info(f"Отримано ID медіа: {video_id}")

            try:
                # Отримуємо список доступних форматів
                format_cmd = [
                    bot.yt_dlp_path,
                    "--no-playlist",
                    # "--cookies",
                    # "cookies.txt",
                    "--list-formats",
                    video_url,
                ]

                process = await asyncio.create_subprocess_exec(
                    *format_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    logger.error(f"Помилка отримання форматів: {stderr.decode()}")
                    return {
                        "message": f"Помилка отримання форматів: {stderr.decode()}",
                        "video_path": None,
                    }

                formats_output = stdout.decode()

                # Базові параметри для завантаження
                base_cmd = [
                    bot.yt_dlp_path,
                    # "--newline",
                    # "--ignore-config",
                    # "--no-playlist",
                    # "--output-na-placeholder",
                    # "NA",
                    "--cookies",
                    "cookies.txt",
                ]

                actual_quality = quality  # Змінна для актуальної якості

                # Логіка вибору формату
                if quality == "mp3":
                    base_cmd.extend(
                        [
                            "-f",
                            "bestaudio",
                            "-x",
                            "--embed-thumbnail",
                            "--audio-format",
                            "mp3",
                        ]
                    )
                elif quality == "audio":
                    base_cmd.extend(["-f", "bestaudio", "-x", "--embed-thumbnail"])
                elif quality == "best":
                    base_cmd.extend(
                        [
                            "-f",
                            "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best",
                        ]
                    )
                else:
                    available_heights = []
                    for line in formats_output.split("\n"):
                        if "mp4" in line and "video only" in line:
                            try:
                                height = int(line.split("x")[1].split()[0])
                                available_heights.append(height)
                            except (IndexError, ValueError):
                                continue

                    if available_heights:
                        # Знаходимо найближчу доступну якість
                        target_height = quality
                        available_heights.sort()
                        if target_height in available_heights:
                            actual_quality = target_height
                        else:
                            # Якщо бажана якість недоступна, беремо найближчу меншу
                            available_heights.sort(reverse=True)
                            actual_quality = available_heights[0]
                            for height in available_heights:
                                if height <= target_height:
                                    actual_quality = height
                                    break

                            logger.info(
                                f"Вибрано якість {actual_quality}p (бажана була {quality}p)"
                            )

                        base_cmd.extend(
                            [
                                "-f",
                                f"bestvideo[height={actual_quality}][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/bestvideo[height={actual_quality}]+bestaudio",
                            ]
                        )
                    else:
                        logger.warning(
                            "Не знайдено відповідних форматів, використовуємо найкращу доступну якість"
                        )
                        base_cmd.extend(["-f", "best[ext=mp4]/best"])
                        actual_quality = "best"

                # Оновлюємо шаблон назви файлу з актуальною якістю
                output_template = os.path.join(
                    youtube_temp_dir, f"{actual_quality}_%(title).200s-%(id)s.%(ext)s"
                )
                base_cmd.extend(["-o", output_template])

                base_cmd.append(video_url)

                process = await asyncio.create_subprocess_exec(
                    *base_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    logger.error(f"Помилка yt-dlp: {stderr.decode()}")
                    return {
                        "message": f"Помилка yt-dlp: {stderr.decode()}",
                        "video_path": None,
                    }

                else:
                    logger.success(f"Завантажено файл: {stdout.decode().strip()}")

                # Шукаємо завантажений файл по ID медіа
                for file in os.listdir(youtube_temp_dir):
                    if video_id in file and file.startswith(f"{actual_quality}_"):
                        file_path = os.path.join(youtube_temp_dir, file)
                        logger.info(f"Знайдено завантажений файл: {file}")
                        return {"message": "Успішно", "video_path": file_path}

                logger.error(f"Файл з ID {video_id} не знайдено")
                return {
                    "message": f"Файл з ID {video_id} не знайдено",
                    "video_path": None,
                }

            except Exception as e:
                logger.error(f"Помилка завантаження медіа: {e}")
                return {
                    "message": f"Помилка завантаження медіа: {e}",
                    "video_path": None,
                }

        except Exception as e:
            logger.warning(f"Спроба {attempt + 1}/{max_retries} не вдалася: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Всі спроби завантаження невдалі: {str(e)}")
                return {
                    "message": f"Помилка завантаження медіа: {str(e)}",
                    "video_path": None,
                }


# Парсинг тегів з повідомлення
def parse_tags(message_text, is_audio=False):
    if is_audio:
        return ["#music"]

    tags = re.findall(r"#\w+", message_text)
    return tags if tags else ["#meme"]


# Основний обробник YouTube-повідомлень
async def youtube_handler(event, external=False, sender_type=None, mode="command"):
    msg = (
        event.message
        if not external
        else await bot.get_messages(event.chat_id, ids=event.message.reply_to_msg_id)
    )

    post = (
        True
        if (
            "-p" in msg.message.join(event.message.message.split(" "))
            or "-p" in event.message.message.split(" ")
            or mode == "service_chat"
        )
        and sender_type == "superadmin"
        else False
    )

    youtube_url_match = re.search(
        r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w-]+)",
        str(msg.message),
    )
    if youtube_url_match:
        youtube_url = youtube_url_match.group(1)
        if external:
            message = await msg.reply("🗿 Опа, ютубчик, ща вкрадемо...")
        else:
            message = await event.reply("🗿 Опа, ютубчик, ща вкрадемо...")

        try:
            quality = get_media_quality(event.message.message)
            result = await download_youtube_media(youtube_url, quality)

            if not result["video_path"]:
                await event.reply(result["message"])
                return

            await bot.edit_message(message, "Скачав медіа, ща завантажимо 👀")
            tags = parse_tags(
                msg.message + " " + event.message.message,
                is_audio=True if quality == "audio" else False,
            )

            total_size = os.path.getsize(result["video_path"])
            caption = f"[Соурс]({youtube_url})"
            if mode == "command":
                username = await get_username(event)
                caption += f" вкрадено у {username}"

            if post:
                caption += f"\n\n" + "\n".join(tags)
                await bot.send_file(
                    bot.channel,
                    caption=caption,
                    file=result["video_path"],
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
                    file=result["video_path"],
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
def get_help_text():
    return (
        "**YouTube [ЛИШЕ АДМІНИ]** - __Опціональні прапори для -d:__\n"
        "    `-p` - __постить дане відео на канал [ЛИШЕ ДЛЯ АДМІНІВ КАНАЛУ]__\n"
        "    `-lq` - __Low quality, буде завантажувати відео з порогом якості в 480p__\n"
        "    `-mq` - __Medium quality (за замовчуванням), буде завантажувати відео з порогом якості в 720p__\n"
        "    `-hq` - __High quality, буде завантажувати відео з порогом якості в 1080p__\n"
        "    `-bq` - __Best quality, буде завантажувати відео з максимально доступною якістю__\n"
        "    `-ea` - __Extract audio, прапор дозволяє завантажити та витягнути аудіо__"
    )


def start_module():
    logger.info("Youtube module started")
    HelpManager.register_help("youtube", get_help_text())

    @bot.on(events.NewMessage(from_users=bot.allowed_users, chats=bot.service_chat_id))
    async def handle_youtube_handler(event):
        await youtube_handler(event, sender_type="superadmin", mode="service_chat")
