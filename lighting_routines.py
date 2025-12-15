import global_vars as gbl
from utils import get_logger
from wrappers.bulb_wrapper import Bulb
from wrappers.WLED_wrapper import WLED

logger = get_logger(__name__)

async def tracking_start():
    """turn off the light"""
    logger.info("Turning off light")
    if not I_HAVE_COMPANY:
        await WLED().turn_off()
        await Bulb().turn_off()

async def bedtime():
    """set the light to a dim, warm colour"""
    logger.info("bedtime")
    await Bulb().turn_on(brightness=20, colortemp=gbl.BEDTIME_COLORTEMP)

async def wake_up(total_time=300):
    """gradually brighten the light over total_time seconds"""
    logger.info("waking up")
    
    await Bulb().turn_on(brightness=100, colortemp=gbl.MAX_COLORTEMP)
    # await Bulb().lerp(10, BEDTIME_COLORTEMP, 100, MAX_COLORTEMP, total_time)

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
    await WLED().turn_on(brightness=5, rgb=(255,0,0))
    await Bulb().turn_on(brightness=5, rgb=(255,0,0))

async def reading_light():
    """set the light to a fairly dim, warm colour"""
    logger.info("turning on reading light")
    await Bulb().turn_on(brightness=10, rgb=(255,0,0))
    await WLED().turn_on(brightness=23, rgb=(255,0,0))

async def set_temp_on_switch():
    try:
        bulb = Bulb() # noqa: F841
    except Exception: # noqa: BLE001
        return

    # state = await bulb.updateState()
    # temp = state.get_temperature()
