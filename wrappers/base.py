import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional

import yaml

from extra_types import ColourType, RGBtype, RGBWWtype
from utils.conversions import temp_to_rgb
from utils.get_logger import get_logger


class FailedConnectionError(Exception):
    """Exception raised when a connection to a device fails."""
    pass

def _ignore_exception(func, ExceptionType: type[Exception]):
    """Decorator to ignore an arbitrary exception in an async method."""
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ExceptionType:
            self.logger.warning("ignored %s in %s", ExceptionType.__name__, func.__name__)
            pass
    return wrapper

    
def ignore_failed_connection(func):
    """Decorator to ignore FailedConnectionError in an async method."""
    return _ignore_exception(func, FailedConnectionError)



class WrapperBase(metaclass=ABCMeta):
    logger = get_logger(__name__)
    
    @property
    @abstractmethod
    def OBJECT_TYPE(self) -> str:
        return ""

    def __init__(self, ip: Optional[str] = None, mac: Optional[str] = None, port: Optional[int] = None):
        # if not self.is_connected:
        #     self.logger.warning("couldn't connect to %s", self.OBJECT_TYPE)
        pass

    @classmethod
    def from_yaml(cls, name: str, yaml_file:str|Path = Path(__file__).parents[1] / "objects.yaml"):
        with open(yaml_file) as f:
            bulbs = yaml.safe_load(f)
            bulb_info:dict = bulbs[name]
            return cls(
                ip=bulb_info["ip"],
                port=bulb_info.get("port", 38899),
                mac=bulb_info["mac"],
            )

    @ignore_failed_connection
    async def turn_on(
        self,
        brightness: Optional[int] = None,
        rgb: ColourType = None,
        colortemp: Optional[int] = None
        ) -> None:
        if colortemp is not None:
            if rgb is not None:
                raise ValueError("cannot provide both rgb and colortemp")
            rgb=self.temp_to_rgb(colortemp)        
        try:
            await self._turn_on(brightness, rgb)
        except Exception as e: # noqa: BLE001
            self.logger.error("couldn't turn on %s: %s", self.OBJECT_TYPE, e)
        self.last_accessed = time.time()

    @abstractmethod
    async def _turn_on(self, brightness: Optional[int], rgb: ColourType) -> None:
        pass

    async def turn_off(self) -> None:
        try:
            await self._turn_off()
            self.last_accessed = time.time()
        except Exception as e: # noqa: BLE001
            self.logger.error("couldn't turn off %s: %s", self.OBJECT_TYPE, e)

    @abstractmethod
    async def _turn_off(self) -> None:
        pass
    
    @abstractmethod
    async def toggle(self) -> None:
        pass

    @property
    @abstractmethod
    async def is_on(self) -> bool:
        pass

    @property
    @abstractmethod
    async def is_connected(self) -> bool:
        pass

    @classmethod
    def temp_to_rgb(cls, temp: int|float) -> RGBtype | RGBWWtype:
        if temp < 1000 or temp > 40000:
            cls.logger.info(
                "Color temperature should be between 1000 and 40000 Kelvin, got %d. "
                "You might get some weird results", temp
            )
        return temp_to_rgb(temp)