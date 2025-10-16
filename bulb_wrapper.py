import math
from pywizlight import wizlight, PilotBuilder, PilotParser
from pywizlight.scenes import get_id_from_scene_name

import logging
import asyncio
from typing import Literal, Optional, Iterator
import operator
SCALING_FACTOR = 1_000_000

light_kwargs = {
    "ip": "192.168.1.100",
    "port": 38899,
    "mac": "cc408525d286",
}

SceneType = Literal[
    "Alarm",
    "Bedtime",
    "Candlelight",
    "Christmas",
    "Cozy",
    "Cool white",
    "Daylight",
    "Diwali",
    "Deep dive",
    "Fall",
    "Fireplace",
    "Forest",
    "Focus",
    "Golden white",
    "Halloween",
    "Jungle",
    "Mojito",
    "Night light",
    "Ocean",
    "Party",
    "Pulse",
    "Pastel colors",
    "Plantgrowth",
    "Romance",
    "Relax",
    "Sunset",
    "Spring",
    "Summer",
    "Steampunk",
    "True colors",
    "TV time",
    "White",
    "Wake-up",
    "Warm white",
    "Rhythm",
]



class Bulb:
    MIN_COLORTEMP = 2200
    MAX_COLORTEMP = 6500
    TIME_STEP = 0.25 # seconds per linear interpolation step

    _light_kwargs = {
    "ip": "192.168.1.100",
    "port": 38899,
    "mac": "cc408525d286",
    }

    logger = logging.getLogger("BulbWrapper")

    def __init__(self, ip: Optional[str] = None, port: Optional[int] = None, mac: Optional[str] = None):
        if ip is None or port is None or mac is None:
            self.light = wizlight(**self._light_kwargs)
        else:
            self.light = wizlight(ip=ip, port=port, mac=mac)

    async def turn_off(self):
        await self.light.turn_off()

    async def turn_on(self, brightness: int, rgb: Optional[tuple[int, int, int]] = None, colortemp: Optional[int] = None):
        if rgb is not None:
            builder = PilotBuilder(brightness=brightness, rgb=rgb)
        if colortemp is not None:
            if rgb is not None:
                raise ValueError("cannot provide both rgb and colortemp")
            builder = PilotBuilder(brightness=brightness, rgb=self.temp_to_rgb(colortemp))
        else:
            raise ValueError("must provide either rgb or colortemp")
        await self.light.turn_on(builder)

    async def set_scene(self, scene: SceneType):
        scene_id = get_id_from_scene_name(scene)
        await self.light.turn_on(PilotBuilder(scene=scene_id))

    async def lerp_temp(self, start_brightness: int, start_temp: int, end_brightness: int, end_temp: int, duration: int):
        """Linearly interpolate between two color temperatures and brightnesses over a given duration.

        Args:
            start_brightness (int): The starting brightness (0-100).
            start_temp (int): The starting color temperature in Kelvin.
            end_brightness (int): The ending brightness (0-100).
            end_temp (int): The ending color temperature in Kelvin.
            duration (int): The total time in seconds over which to perform the interpolation.
        """
        steps = round(duration / self.TIME_STEP)
        brightness_iter = get_range(start_brightness, end_brightness, steps)
        temp_iter = get_range(start_temp, end_temp, steps)
        assert operator.length_hint(brightness_iter) == operator.length_hint(temp_iter)

        for brightness, temp in zip(brightness_iter, temp_iter):
            await self.turn_on(brightness=brightness, colortemp=temp)
            await asyncio.sleep(self.TIME_STEP)

    async def updateState(self) -> Optional[PilotParser]:
        return await self.light.updateState()

    @classmethod
    def temp_to_rgb(cls, temp) -> tuple[int, int, int]:
        """Convert color temperature in Kelvin to RGB values.

        Algorithm from Tanner Helland (http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/)
        """
        # if temp < 1000 or temp > 40000:
        #     cls.logger.warning("Color temperature should be between 1000 and 40000 Kelvin, got %d. " \
        #     "You might get some weird results", temp)
        
        temp = temp / 100

        if temp <= 66:
            red = 255
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
            blue = 255

        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))

        return round(red), round(green), round(blue)
    

def get_range(start: int, stop: int, length: int) -> Iterator[int]:
    # multiply then divide by SCALING_FACTOR to avoid issues with `step` rounding to zero.
    # it is possible to calculate the ideal SCALING_FACTOR,
    # but is simpler to just use an arbitrarily large constant
    start = start * SCALING_FACTOR
    stop = stop * SCALING_FACTOR
    span = abs(stop - start)
    step = round((span / length))
    assert step > 0
    iterator = range(start, stop + step, step)
    assert operator.length_hint(iterator) == length + 1
    ret = map(lambda x: round(x / SCALING_FACTOR), iterator)
    setattr(ret, "__length_hint__", length + 1)
    return ret
