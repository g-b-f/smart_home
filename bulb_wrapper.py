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
        elif colortemp is not None:
            if colortemp < self.MIN_COLORTEMP or colortemp > self.MAX_COLORTEMP:
                # outside of supported range, convert to rgb
                builder = PilotBuilder(brightness=brightness, rgb=self.temp_to_rgb(colortemp))
            else:
                builder = PilotBuilder(brightness=brightness, colortemp=colortemp)
        else:
            raise ValueError("must provide either rgb or colortemp")
        await self.light.turn_on(builder)

    async def set_scene(self, scene: SceneType):
        scene_id = get_id_from_scene_name(scene)
        await self.light.turn_on(PilotBuilder(scene=scene_id))

    
    @classmethod
    def temp_to_rgb(cls, temp) -> tuple[int, int, int]:
        """Convert color temperature in Kelvin to RGB values.

        Algorithm from Tanner Helland (http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/)
        """
        if temp < 1000 or temp > 40000:
            cls.logger.warning("Color temperature should be between 1000 and 40000 Kelvin, got %d. " \
            "You might get some weird results", temp)
        
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
    
