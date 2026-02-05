import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json


import astral.sun

import global_vars as gbl
from extra_types import RGBtype

MAX_LOG_SIZE_BYTES = 1024 * 1024 # 1 MB

class JsonWrapper:
    def __init__(self, file: Path):
        self.file = file
    
    @property
    def data(self):
        return json.loads(self.file.read_text())

    @data.setter
    def data(self, d):
        self.file.write_text(json.dumps(d))

    def __setattr__(self, key, val):
        d = self.data
        d[key] = val
        self.data = d
    
    def __getattr__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data
    
    def __iter__(self):
        yield from self.data.items()

    def __len__(self):
        return len(self.data)

mutable_globals = JsonWrapper(Path(__file__).parent / "mutable_globals.json")


def get_logger(name: str, level=None) -> logging.Logger:
    if level is None:
        level = gbl.LOG_LEVEL
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


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def rgb_to_hex(rgb: RGBtype) -> str:
    return "{:02X}{:02X}{:02X}".format(*rgb)


def hex_to_rgb(hex_colour: str) -> RGBtype:
    hex_colour = hex_colour.lstrip('#')
    if len(hex_colour) == 3:
        hex_colour = ''.join([c*2 for c in hex_colour])
    if len(hex_colour) != 6:
        raise ValueError("Hex color must be in the format RRGGBB or RGB")
    r = int(hex_colour[0:2], 16)
    g = int(hex_colour[2:4], 16)
    b = int(hex_colour[4:6], 16)
    return (r, g, b)


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
