import math
import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Optional, cast

import yaml

from extra_types import RGBtype
from utils import clamp, get_logger


class WrapperBase(metaclass=ABCMeta):

    logger = get_logger(__name__)
    
    @property
    @abstractmethod
    def OBJECT_TYPE(self):
        pass

    def __init__(self, ip: Optional[str] = None, port: Optional[int] = None, mac: Optional[str] = None):
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
 
    async def turn_on(self, brightness: Optional[int] = None, rgb: Optional[RGBtype] = None, colortemp: Optional[int] = None) -> None:
        if colortemp is not None:
            if rgb is not None:
                raise ValueError("cannot provide both rgb and colortemp")
            rgb=self.temp_to_rgb(colortemp)        
        try:
            await self._turn_on(brightness, rgb)
        except Exception as e: # noqa: BLE001
            self.logger.error("couldn't turn on %s: %s", self.OBJECT_TYPE, e)
        self.last_accessed = time.time()
        pass

    @abstractmethod
    async def _turn_on(self, brightness: Optional[int], rgb: Optional[RGBtype]) -> None:
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
    async def is_connected(self):
        try:
            await self.get_info()
            return True
        except Exception: # noqa: BLE001
            return False
        
    @abstractmethod
    async def get_info(self) -> Any:
        pass
        

    @classmethod
    def temp_to_rgb(cls, temp: int|float) -> RGBtype:
        """Convert color temperature in Kelvin to RGB values.

        Algorithm from Tanner Helland (http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/)
        """
        if temp < 1000 or temp > 40000:
            cls.logger.info("Color temperature should be between 1000 and 40000 Kelvin, got %d. " \
            "You might get some weird results", temp)
        
        temp = cast(float, temp / 100)

        if temp <= 66:
            red = 255.0
            green = temp
            green = 99.4708025861 * math.log(green) - 161.1195681661
            if temp <= 19:
                blue = 0.0
            else:
                blue = temp - 10.0
                blue = 138.5177312231 * math.log(blue) - 305.0447927307
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
            blue = 255.0

        red = clamp(red, 0.0, 255.0)
        green = clamp(green, 0.0, 255.0)
        blue = clamp(blue, 0.0, 255.0)

        return round(red), round(green), round(blue)  