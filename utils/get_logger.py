import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import global_vars as gbl

MAX_LOG_SIZE_BYTES = 1024 * 1024 # 1 MB

def namer(default_name: str) -> str:
    """By default, `RotatingFileHandler` creates logs of the form `log.txt.1`.
    This custom namer instead makes them of the form `log_1.txt`"""

    default_path = Path(default_name)
    index = default_path.suffix.strip(".")
    base_file = Path(default_path.stem)
    new_name = f"{base_file.stem}_{index}{base_file.suffix}"
    return str(default_path.parent / new_name)

def get_logger(name: str, level=None) -> logging.Logger:
    if level is None:
        level = gbl.LOG_LEVEL
    if level.upper() not in logging._nameToLevel:
        raise ValueError(f"Invalid log level: {level}")
    level_int = logging._nameToLevel[level.upper()]

    log_file = Path(__file__).parent.parent / "log.txt"
    handler = RotatingFileHandler(log_file, maxBytes=MAX_LOG_SIZE_BYTES, backupCount=2)
    handler.setLevel(level_int)
    handler.namer = namer
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level_int)
    logger.addHandler(handler)

    return logger
