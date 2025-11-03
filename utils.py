import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

MAX_LOG_SIZE_BYTES = 1024 * 1024

def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    log_file = Path(__file__).parent / "log.txt"
    handler = RotatingFileHandler(log_file, maxBytes=MAX_LOG_SIZE_BYTES, backupCount=2)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
