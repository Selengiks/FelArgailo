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
                    logger.trace(f"Deleted file: {file_path}")
            for folder in folders:
                dir_path = os.path.join(root, folder)

                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    is_smth_deleted = True
                    logger.trace(f"Deleted empty dir: {dir_path}")
        if is_smth_deleted:
            logger.info("Temp files and dirs successfully deleted.")

    except Exception as e:
        logger.error(f"Error occurred until deleting temp files and dirs: {e}")
