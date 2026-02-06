import asyncio
import operator
import sys
import time
from pathlib import Path
from typing import Iterator, Optional

from pywizlight import (  # type: ignore[import-untyped]
    PilotBuilder,
    PilotParser,
    scenes,
    wizlight,
)
from pywizlight.exceptions import (
    WizLightConnectionError,  # type: ignore[import-untyped]
)

from utils import clamp, get_logger, mutable_globals

sys.path.append(str(Path(__file__).parent))
from extra_types import RGBtype, SceneType
from wrappers.base import WrapperBase

SCALING_FACTOR = 1_000_000


class Bulb(WrapperBase):
    MIN_COLORTEMP = 2200
    MAX_COLORTEMP = 6500
    TIME_STEP = 0.25 # seconds per linear interpolation step
    BULB_NAME = "bedroom_light"

    OBJECT_TYPE = "bulb" # type: ignore[reportAssignmentType]
    logger = get_logger(__name__)  # type: ignore[reportAssignmentType]

    def __init__(self, ip: Optional[str] = None, port: Optional[int] = None, mac: Optional[str] = None):
        if ip is None or port is None or mac is None:
            self.light:wizlight = self.from_yaml(self.BULB_NAME).light
        else:
            self.light = wizlight(ip=ip, port=port, mac=mac)
            self.ip = ip
            self.port = port
            self.mac = mac

#        try:
#            self.last_state = self.async_to_sync(self.light.updateState()) # check connection
#        except RuntimeError: # event loop already running
            self.last_state = None

        self.last_accessed = time.time()

    async def _turn_off(self):
        if not mutable_globals.use_bulb:
            self.logger.debug("not turning off bulb due to global setting")
            return

        await self.light.turn_off()

    async def _turn_on(self, brightness: Optional[int] = None, rgb: Optional[RGBtype] = None):
        if not mutable_globals.use_bulb:
            self.logger.debug("not turning on bulb due to global setting")
            return
        if brightness is not None:
            brightness = self.clamp_brightness(brightness)        
        await self.light.turn_on(PilotBuilder(brightness=brightness, rgb=rgb))

    async def set_scene(self, scene: SceneType, brightness: Optional[int] = None, speed: Optional[int] = None):
        """Set the bulb to a predefined scene.

        Args:
            scene (SceneType): Name of the scene to set.
            brightness (int, optional): Brightness (10-100). Defaults to None.
            speed (int, optional): Speed of effect (10-200). Defaults to None.
        """
        if not mutable_globals.use_bulb:
            self.logger.debug("not turning on bulb due to global setting")
            return

        scene_id = scenes.get_id_from_scene_name(scene)
        if brightness is not None:
            brightness = self.clamp_brightness(brightness)
        if speed is not None:
            speed = self.clamp_speed(speed)
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
        start_brightness = self.clamp_brightness(start_brightness)
        end_brightness = self.clamp_brightness(end_brightness)
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
    
    async def get_info(self):
        return await self.updateState()
    
    @property
    async def is_connected(self) -> bool:
        try:
            await self.get_info()
            return True
        except WizLightConnectionError:
            return False

    @property
    async def is_on(self) -> bool:
        state = await self.light.updateState()
        if state is None:
            self.logger.error("couldn't get state in is_on")
            return False
        ret = state.get_state()
        if ret is None:
            self.logger.error("couldn't get state in is_on")
            return False
        return ret
    
    async def toggle(self):
        if self.is_on:
            await self.turn_off()
        else:
            await self.turn_on()  

    def clamp_brightness(self, value: int) -> int:
        """Clamp brightness value between 10 and 100."""
        return clamp(value, 10, 100)

    def clamp_speed(self, value: int) -> int:
        """Clamp speed value between 10 and 200."""
        return clamp(value, 10, 200)
  

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
