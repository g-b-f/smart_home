from pywizlight import wizlight, PilotBuilder, PilotParser
import logging
import asyncio
from typing import Optional, Iterator
RANGE_MULTIPLIER = 1_000_000


light_kwargs = {
    "ip": "192.168.1.100",
    "port": 38899,
    "mac": "cc408525d286",
}

MIN_COLORTEMP = 2200
MAX_COLORTEMP = 6500
TEMP_STEP = 100

class Routine:
    @staticmethod
    async def turn_off_light():
        """turn off the light"""
        light = wizlight(**light_kwargs)
        await light.turn_off()

    @staticmethod
    async def bedtime():
        """set the light to a dim, warm color"""
        light = wizlight(**light_kwargs)
        await light.turn_on(PilotBuilder(brightness=10, rgb=(255, 96, 0)))

    @staticmethod
    async def wake_up(total_time=300, time_step=0.3):
        """gradually brighten the light over total_time seconds"""
        light = wizlight(**light_kwargs)
        iterations = round(total_time/time_step)
        temp_iter = get_range(MIN_COLORTEMP, MAX_COLORTEMP, iterations)
        brightness_iter = get_range(10, 100, iterations)
        
        for temp, brightness in zip(temp_iter, brightness_iter):
            await light.turn_on(PilotBuilder(brightness=brightness, colortemp=temp))
            await asyncio.sleep(time_step)

    @staticmethod
    async def sync_colour_temp(desired_temp: int):
        light = wizlight(**light_kwargs)
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

        if temp < desired_temp:
            settings = PilotBuilder(brightness=brightness, colortemp=temp + TEMP_STEP)
            await light.turn_on(settings)
            return
        elif temp > desired_temp:
            settings = PilotBuilder(brightness=brightness, colortemp=temp - TEMP_STEP)
            await light.turn_on(settings)
            return
        else: # current_temp == desired_temp
            return


def get_range(start:int, stop:int, iterations:int) -> Iterator[int]:
    # multiply then divide by RANGE_MULTIPLIER to avoid issues with `step` rounding to zero.
    # it is possible to calculate the ideal RANGE_MULTIPLIER,
    # but is simpler to just use an arbitrarily large constant
    start = start * RANGE_MULTIPLIER
    stop = stop * RANGE_MULTIPLIER
    span = abs(stop - start)
    step = round((span / iterations))
    assert step > 0
    iterator = range(start, stop +step, step)
    return map(lambda x: round(x/ RANGE_MULTIPLIER), iterator)