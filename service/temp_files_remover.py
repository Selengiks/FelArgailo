import os
from service.bot import bot
from loguru import logger


async def cleanup_temp_files():
    is_smth_deleted = False

    try:
        for root, folders, files in os.walk(bot.temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    is_smth_deleted = True
                    logger.trace(f"Видалено файл: {file_path}")
            for folder in folders:
                dir_path = os.path.join(root, folder)

                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    is_smth_deleted = True
                    logger.trace(f"Видалено порожню директорію: {dir_path}")
        if is_smth_deleted:
            logger.info("Тимчасові папки та файли видалено.")

    except Exception as e:
        logger.error(f"Сталася помилка під час видалення: {e}")
