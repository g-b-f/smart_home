from pywizlight import PilotParser  # type: ignore[import-untyped]
import logging
from typing import Optional
from bulb_wrapper import Bulb
SCALING_FACTOR = 1_000_000


light_kwargs = {
    "ip": "192.168.1.100",
    "port": 38899,
    "mac": "cc408525d286",
}

MIN_COLORTEMP = 2200
MAX_COLORTEMP = 6500
TEMP_STEP = 100
BEDTIME_COLORTEMP = 1320

class Routine:
    @staticmethod
    async def turn_off_light():
        """turn off the light"""
        await Bulb().turn_off()

    @staticmethod
    async def bedtime():
        """set the light to a dim, warm color"""
        await Bulb().turn_on(brightness=10, colortemp=BEDTIME_COLORTEMP)

    @staticmethod
    async def wake_up(total_time=300):
        """gradually brighten the light over total_time seconds"""
        await Bulb().lerp_temp(10, BEDTIME_COLORTEMP, 100, MAX_COLORTEMP, total_time)

    @staticmethod
    async def sync_colour_temp(desired_temp: int):
        light = Bulb()
        state: Optional[PilotParser] = await light.updateState()
        if state is None:
            logging.error("couldn't get state")
            return
        if not state.get_state():
            return
        brightness = state.get_brightness()
        temp = state.get_colortemp()
        if temp is None or brightness is None:
            logging.error("couldn't get color temp or brightness")
            return
        
        await light.lerp_temp(brightness, temp, brightness, desired_temp, 10)