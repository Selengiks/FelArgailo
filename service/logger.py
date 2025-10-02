# service/logger.py

import sys
import logging
from loguru import logger

LOGGER_MODE = "INFO"  # TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL

LOGGING_LEVELS = {
    "TRACE": logging.DEBUG,  # У logging нема TRACE, тому кидаємо на DEBUG
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logger():
    logger.remove()
    logger.add(
        "logs/log_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="14 days",
        level=LOGGER_MODE,
    )

    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:DD.MM.YY H:mm:ss}</green> | <level>{level}</level> | <magenta>{file}:{line}</magenta> | <level>{message}</level>",
        level=LOGGER_MODE,
    )

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            level = record.levelname
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(level, record.getMessage())

    logging_level = LOGGING_LEVELS.get(LOGGER_MODE, logging.DEBUG)

    logging.basicConfig(handlers=[InterceptHandler()], level=logging_level)
    logging.getLogger("telethon").handlers = [InterceptHandler()]
    logging.getLogger("telethon").propagate = False

    logger.info("Logger initialized on level: " + LOGGER_MODE)
