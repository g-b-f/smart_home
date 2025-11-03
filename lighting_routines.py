from bulb_wrapper import Bulb
from utils import get_logger
import globals

logger = get_logger(__name__)

class Routine:
    @staticmethod
    async def tracking_start():
        """turn off the light"""
        logger.info("Turning off light")
        await Bulb().turn_off()

    @staticmethod
    async def bedtime():
        """set the light to a dim, warm color"""
        logger.info("bedtime")
        await Bulb().turn_on(brightness=20, colortemp=globals.BEDTIME_COLORTEMP)

    @staticmethod
    async def wake_up(total_time=300):
        """gradually brighten the light over total_time seconds"""
        logger.info("waking up")
        
        await Bulb().turn_on(brightness=100, colortemp=globals.MAX_COLORTEMP)
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