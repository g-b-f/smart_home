import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import astral.sun
from pydantic import ValidationError

import global_vars as gbl
from extra_types import MutableGlobals, RGBtype

MAX_LOG_SIZE_BYTES = 1024 * 1024 # 1 MB


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

logger = get_logger(__name__)

class JsonWrapper:

    default = MutableGlobals.model_construct().model_dump()

    def __init__(self, file: Path):
        self.file = file
        self.logger = get_logger(file.stem)

    @staticmethod
    def format_iso(obj):
        return obj.isoformat() if isinstance(obj, datetime) else obj

    def write_default(self):
        logger.info(
            "writing default values:\n%s",
            json.dumps(self.default, indent=4, default=self.format_iso)
        )
        self.file.write_text(json.dumps(self.default, default=self.format_iso))
        
    @property
    def data(self) -> dict:
        try:
            ret = json.loads(self.file.read_text())
            MutableGlobals.model_validate(ret)
        except (FileNotFoundError, ValidationError) as e:
            logger.error("Error loading %s: %s. Reverting to default.", self.file.name, e)
            self.write_default()
            ret = self.default
        return ret

    @data.setter
    def data(self, d):
        self.file.write_text(json.dumps(d, indent=4))
    
    def _get_var(self, key:str):
        ret = self.data[key]
        self.logger.debug("%s is %s", key, ret)
        return ret
    
    def _set_var(self, key:str, val):
        data = self.data
        data[key] = val
        self.data = data

    @property
    def visitor_present(self) -> bool:
        return self._get_var("visitor_present")
    
    @visitor_present.setter
    def visitor_present(self, val:bool):
        self._set_var("visitor_present", val)

    @property
    def use_bulb(self) -> bool:
        return self._get_var("use_bulb")
    
    @use_bulb.setter
    def use_bulb(self, val:bool):
        self._set_var("use_bulb", val)
    
    @property
    def use_wled(self) -> bool:
        return self._get_var("use_wled")
    
    @use_wled.setter
    def use_wled(self, val:bool):
        self._set_var("use_wled", val)

    @property
    def last_sleep(self) -> datetime:
        return datetime.fromisoformat(self._get_var("last_sleep"))
    
    @last_sleep.setter
    def last_sleep(self, val:datetime):
        self._set_var("last_sleep", val.isoformat())
    
    def __contains__(self, key):
        return key in self.data
    
    def __iter__(self):
        yield from self.data.items()

    def __len__(self):
        return len(self.data)
    
    def __repr__(self) -> str:
        return str(self.data)

mutable_globals = JsonWrapper(Path(__file__).parent / "mutable_globals.json")


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


if __name__ == "__main__":
    mutable_globals.write_default()