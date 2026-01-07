import os
from typing import Tuple
from service.bot import bot
from loguru import logger


async def cleanup_temp_files() -> Tuple[int, int]:
    """
    Асинхронна функція для очищення тимчасових файлів та директорій.

    Returns:
        Tuple[int, int]: Кількість видалених файлів та директорій
    """
    files_deleted = 0
    dirs_deleted = 0

    if not os.path.exists(bot.temp_dir):
        logger.warning(f"Тимчасова директорія не існує: {bot.temp_dir}")
        return files_deleted, dirs_deleted

    try:
        for root, dirs, files in os.walk(bot.temp_dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, "rb"):
                                pass
                        except PermissionError:
                            logger.warning(
                                f"Файл використовується іншим процесом: {file_path}"
                            )
                            continue

                        os.remove(file_path)
                        files_deleted += 1
                        logger.trace(f"Видалено файл ({files_deleted}): {file_path}")
                except (PermissionError, OSError) as e:
                    logger.error(f"Помилка при видаленні файлу {file_path}: {e}")

            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if os.path.islink(dir_path):
                        logger.warning(f"Пропущено символічне посилання: {dir_path}")
                        continue

                    if os.path.exists(dir_path) and not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        dirs_deleted += 1
                        logger.trace(
                            f"Видалено порожню директорію ({dirs_deleted}): {dir_path}"
                        )
                except (PermissionError, OSError) as e:
                    logger.error(f"Помилка при видаленні директорії {dir_path}: {e}")

        if files_deleted > 0 or dirs_deleted > 0:
            logger.info(
                f"Очищення завершено. Видалено файлів: {files_deleted}, директорій: {dirs_deleted}"
            )
        else:
            logger.info("Немає файлів для видалення")

    except Exception as e:
        logger.error(f"Критична помилка під час очищення тимчасової директорії: {e}")

    return files_deleted, dirs_deleted
