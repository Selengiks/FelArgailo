# service/logger.py

from sys import stdout
from loguru import logger


class Logger:
    def __init__(self, mode):
        logger.remove()
        logger.add("logs/log_{time}.log", rotation="1 day", level=mode)

        logger.add(
            stdout,
            colorize=True,
            format="<green>{time:DD.MM.YY H:mm:ss}</green> "
            "| <level>{level}</level> | <magenta>{file}:{line}</magenta> | <level>{"
            "message}</level>",
            level=mode,
        )

        logger.info("Logger configs updated")


def start_logger(mode):
    Logger(mode)
