import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import astral
import astral.sun

import global_vars as gbl

MAX_LOG_SIZE_BYTES = 1024 * 1024 # 1 MB

def get_logger(name: str, level="INFO") -> logging.Logger:
    if level.upper() not in logging._nameToLevel:
        raise ValueError(f"Invalid log level: {level}")
    level_int = logging._nameToLevel[level.upper()]

    log_file = Path(__file__).parent / "log.txt"
    handler = RotatingFileHandler(log_file, maxBytes=MAX_LOG_SIZE_BYTES, backupCount=2)
    handler.setLevel(level_int)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level_int)
    logger.addHandler(handler)

    return logger

def get_zenith(location = astral.LocationInfo()) -> float:
    return astral.sun.zenith(location.observer)


def get_colourtemp_for_time(location = astral.LocationInfo(), date=None) -> int:
    sun = Sun(location, date)
    now = astral.now(location.tzinfo)

    if now < sun.dawn or now > sun.dusk:
        return gbl.NIGHT_COLOURTEMP
    elif sun.dawn <= now < sun.sunrise:
        return gbl.SUNRISE_COLOURTEMP
    elif sun.sunrise <= now < sun.sunset:
        return gbl.DAY_COLOURTEMP
    elif sun.sunset <= now < sun.dusk:
        return gbl.SUNSET_COLOURTEMP
    else:
        return gbl.SUNSET_COLOURTEMP

class Sun:
    def __init__(self, location = astral.LocationInfo(), date=None):
        self.location = location
        if date is None:
            self.date = astral.today(location.tzinfo)
        self.sun = astral.sun.sun(location.observer, date, tzinfo=self.location.tzinfo)

    def __getattribute__(self, name: str):
        if name in {"dawn", "sunrise", "noon", "sunset", "dusk"}:
            return self.sun[name]
        return super().__getattribute__(name)

    def __repr__(self):
        return f"Sun({self.location}): {self.sun}"
