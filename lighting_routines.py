from utils import get_logger
from bulb_wrapper import Bulb

logger = get_logger(__name__)

SCALING_FACTOR = 1_000_000

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
        await Bulb().turn_on(brightness=100, colortemp=MAX_COLORTEMP)
        # await Bulb().lerp(10, BEDTIME_COLORTEMP, 100, MAX_COLORTEMP, total_time)

    @staticmethod
    async def sync_colour_temp(desired_temp: int):
        light = Bulb()
        state = await light.updateState()
        if state is None:
            logger.error("couldn't get state")
            return
        if not state.get_state():
            return
        brightness = state.get_brightness()
        temp = state.get_colortemp()
        if temp is None or brightness is None:
            logger.error("couldn't get color temp or brightness")
            return
        
        await light.lerp(brightness, temp, brightness, desired_temp, 10)