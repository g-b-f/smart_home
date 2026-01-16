from datetime import datetime

import global_vars as gbl
from utils import get_logger
from wrappers.bulb_wrapper import Bulb
from wrappers.WLED_wrapper import WLED

logger = get_logger(__name__)

async def tracking_start():
    """turn off the light"""
    logger.info("Turning off light")
    # await WLED().turn_off()
    await Bulb().turn_off()

async def snooze():
    """snooze alarm"""
    if not gbl.IS_VISITOR_PRESENT:
        logger.info("snoozing")
        await Bulb().turn_on(brightness=50, colortemp=gbl.MAX_COLORTEMP)
    
async def bedtime():
    """set the light to a dim, warm colour"""
    logger.info("bedtime")
    await Bulb().turn_on(brightness=20, colortemp=gbl.BEDTIME_COLORTEMP)

async def wake_up(total_time=300):
    """gradually brighten the light over total_time seconds"""
    if not gbl.IS_VISITOR_PRESENT:
        logger.info("waking up")
        await Bulb().turn_on(brightness=100, colortemp=gbl.MAX_COLORTEMP)
    # await Bulb().lerp(10, BEDTIME_COLORTEMP, 100, MAX_COLORTEMP, total_time)

async def tracking_stopped():
    current_time = datetime.now().time()
    """called when sleep tracking stops"""
    if gbl.IS_VISITOR_PRESENT:
        logger.info("visitor present, not turning on light")
        return "OK", 200

    if current_time > gbl.WAKE_UP_TIME:
        logger.debug(
                "%s is greater than %s, turning on light",
                current_time, gbl.WAKE_UP_TIME
                )
        await wake_up()
    else:
        logger.debug(
                "%s is less than %s, turning on nightlight",
                current_time, gbl.WAKE_UP_TIME
                )
        

        await nightlight()

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
        logger.error("couldn't get colour temp or brightness")
        return
    
    await light.lerp(brightness, temp, brightness, desired_temp, 10)

async def nightlight():
    """set the light to a very dim, warm colour"""
    logger.info("turning on nightlight")
    if gbl.USE_WLED:
        await WLED().turn_on(brightness=5, rgb=(255,0,0))
    else:
        logger.debug("not turning on WLED due to global settimg")
    if gbl.USE_BULB:
        await Bulb().turn_on(brightness=5, rgb=(255,0,0))
    else:
        logger.debug("not turning on bulb due to global settimg")

async def reading_light():
    """set the light to a fairly dim, warm colour"""
    logger.info("turning on reading light")
    if gbl.USE_BULB:
        await Bulb().turn_on(brightness=10, rgb=(255,0,0))
    else:
        logger.debug("not turning on bulb due to global settimg")
    if gbl.USE_WLED:
        await WLED().turn_on(brightness=23, rgb=(255,0,0))
    else:
        logger.debug("not turning on WLED due to global settimg")

async def set_temp_on_switch():
    try:
        bulb = Bulb() # noqa: F841
    except Exception: # noqa: BLE001
        return

    # state = await bulb.updateState()
    # temp = state.get_temperature()
