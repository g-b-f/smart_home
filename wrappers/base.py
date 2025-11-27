import math
from abc import ABCMeta, abstractmethod
from typing import cast

from extra_types import RGBtype
from utils import clamp, get_logger

_logger = get_logger(__name__)

class WrapperBase(metaclass=ABCMeta):
 
    @abstractmethod
    async def turn_on(self) -> None:
        pass
    @abstractmethod
    async def turn_off(self) -> None:
        pass
    @abstractmethod
    async def toggle(self) -> None:
        pass

    @property
    @abstractmethod
    async def is_on(self) -> bool:
        pass

    @staticmethod
    def temp_to_rgb(temp: int|float) -> RGBtype:
        """Convert color temperature in Kelvin to RGB values.

        Algorithm from Tanner Helland (http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/)
        """
        if temp < 1000 or temp > 40000:
            _logger.info("Color temperature should be between 1000 and 40000 Kelvin, got %d. " \
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