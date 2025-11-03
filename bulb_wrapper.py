import asyncio
import math
import operator
import sys
import time
from pathlib import Path
from typing import Iterator, Optional, cast

import yaml
from pywizlight import (  # type: ignore[import-untyped]
    PilotBuilder,
    PilotParser,
    scenes,
    wizlight,
)

from utils import get_logger

sys.path.append(str(Path(__file__).parent))
from extra_types import RGBtype, SceneType

SCALING_FACTOR = 1_000_000


class Bulb:
    MIN_COLORTEMP = 2200
    MAX_COLORTEMP = 6500
    TIME_STEP = 0.25 # seconds per linear interpolation step
    BULB_NAME = "bedroom_light"

    logger = get_logger(__name__)

    @staticmethod
    def from_yaml(name: str, yaml_file="objects.yaml") -> "Bulb":
        with open(Path(__file__).parent / yaml_file) as f:
            bulbs = yaml.safe_load(f)
            bulb_info = bulbs[name]
            return Bulb(
                ip=bulb_info["ip"],
                port=bulb_info.get("port", 38899),
                mac=bulb_info["mac"],
            )

    def __init__(self, ip: Optional[str] = None, port: Optional[int] = None, mac: Optional[str] = None):

        if ip is None or port is None or mac is None:
            self.light:wizlight = self.from_yaml(self.BULB_NAME).light
        else:
            self.light = wizlight(ip=ip, port=port, mac=mac)

        try:
            self.last_state = asyncio.run(self.light.updateState()) # check connection
        except RuntimeError: # event loop already running
            self.last_state = None

        self.last_accessed = time.time()

    async def turn_off(self):
        await self.light.turn_off()
        self.last_accessed = time.time()

    async def turn_on(self, brightness: Optional[int] = None, rgb: Optional[RGBtype] = None, colortemp: Optional[int] = None):
        if rgb is not None:
            builder = PilotBuilder(brightness=brightness, rgb=rgb)
        if colortemp is not None:
            if rgb is not None:
                raise ValueError("cannot provide both rgb and colortemp")
            builder = PilotBuilder(brightness=brightness, rgb=self.temp_to_rgb(colortemp))
        else:
            builder = PilotBuilder()
        
        await self.light.turn_on(builder)
        self.last_accessed = time.time()

    async def set_scene(self, scene: SceneType, brightness: Optional[int] = None, speed: Optional[int] = None):
        """Set the bulb to a predefined scene.

        Args:
            scene (SceneType): Name of the scene to set.
            brightness (int, optional): Brightness (10-100). Defaults to None.
            speed (int, optional): Speed of effect (10-200). Defaults to None.
        """
        scene_id = scenes.get_id_from_scene_name(scene)
        if brightness is not None:
            brightness = max(10, min(100, brightness))
        if speed is not None:
            speed = max(10, min(200, speed))
        await self.light.turn_on(PilotBuilder(scene=scene_id, brightness=brightness, speed=speed))

    async def lerp(self, start_brightness: int, start_temp: int, end_brightness: int, end_temp: int, duration: int):
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
        # assert operator.length_hint(brightness_iter) == operator.length_hint(temp_iter)

        for brightness, temp in zip(brightness_iter, temp_iter):
            state = await self.updateState()
            if state is None or self.last_state is None:
                self.logger.error("couldn't get state during lerp, setting to final values")
                await self.turn_on(brightness=end_brightness, colortemp=end_temp)
                return
            
            same_brightness = brightness == state.get_brightness() and state.get_brightness() is not None
            same_rgb = state.get_rgb() == self.last_state.get_rgb() and state.get_rgb() is not None
            same_temp = state.get_colortemp() == self.last_state.get_colortemp() and state.get_colortemp() is not None

            if not (state.get_state() and same_brightness and (same_rgb or same_temp)):
                self.logger.info("lerp interrupted due to external change")
                return

            await self.turn_on(brightness=brightness, colortemp=temp)
            self.last_state = await self.updateState()

            await asyncio.sleep(self.TIME_STEP)

    async def updateState(self) -> Optional[PilotParser]:
        return await self.light.updateState()

    @classmethod
    def temp_to_rgb(cls, temp: int|float) -> RGBtype:
        """Convert color temperature in Kelvin to RGB values.

        Algorithm from Tanner Helland (http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/)
        """
        if temp < 1000 or temp > 40000:
            cls.logger.warning("Color temperature should be between 1000 and 40000 Kelvin, got %d. " \
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
    ret = (round(x / SCALING_FACTOR) for x in iterator)
    # setattr(ret, "__length_hint__", length + 1)
    return ret
