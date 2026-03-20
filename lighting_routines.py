from datetime import datetime

import global_vars as gbl
from utils import format_time as fmt
from utils import get_logger, mutable_globals
from wrappers.bulb_wrapper import Bulb
from wrappers.WLED_wrapper import WLED

logger = get_logger(__name__)

async def tracking_start():
    """turn off the light"""
    logger.info("Turning off light")
    if datetime.now().time() > gbl.EARLIEST_SLEEP_TIME:
        now = datetime.now()
        logger.debug(
            "setting last sleep time to %s", now.strftime("%d/%m/%Y %H:%M:%S")
            )
        mutable_globals.last_sleep = now

    if mutable_globals.use_wled:
        await WLED().turn_off()

    if mutable_globals.use_bulb:
        await Bulb().turn_off()

async def snooze():
    """snooze alarm"""
    if not mutable_globals.visitor_present:
        logger.info("snoozing")
        await Bulb().turn_on(brightness=50, colortemp=gbl.MAX_COLORTEMP)
    
async def bedtime():
    """set the light to a dim, warm colour"""
    logger.info("bedtime")
    await Bulb().turn_on(brightness=20, colortemp=gbl.BEDTIME_COLORTEMP)

async def wake_up(total_time=300):
    """gradually brighten the light over total_time seconds"""
    if not mutable_globals.visitor_present:
        logger.info("waking up")
        await Bulb().turn_on(brightness=100, colortemp=gbl.MAX_COLORTEMP)
    # await Bulb().lerp(10, BEDTIME_COLORTEMP, 100, MAX_COLORTEMP, total_time)

async def nightlight():
    """set the light to a very dim, warm colour"""
    logger.info("turning on nightlight")
    if mutable_globals.use_bulb:
        await Bulb().turn_on(brightness=5, rgb=(255,0,0))
    if mutable_globals.use_wled:
        await WLED().turn_on(brightness=5, rgb=(255,0,0))

async def reading_light():
    """set the light to a fairly dim, warm colour"""
    logger.info("turning on reading light")
    if mutable_globals.use_bulb:
        await Bulb().turn_on(brightness=10, rgb=(255,0,0))
    if mutable_globals.use_wled:
        await WLED().turn_on(brightness=23, rgb=(255,0,0))

async def tracking_stopped():
    current_time = datetime.now().time()
    """called when sleep tracking stops"""
    if mutable_globals.visitor_present:
        logger.info("visitor present, not turning on light")
        return "OK", 200

    if current_time > gbl.LATE_WAKE_UP_TIME:
        logger.info(
                "current time %s is greater than late wakeup time %s, turning on light",
                fmt(current_time), fmt(gbl.LATE_WAKE_UP_TIME)
                )
        await wake_up()
    elif current_time < gbl.EARLY_WAKE_TIME:
        logger.info(
                "current time %s is less than early wakeup time %s,",
                fmt(current_time), fmt(gbl.EARLIEST_SLEEP_TIME)
                )
        await nightlight()

    else:
        sleep_length = datetime.now() - mutable_globals.last_sleep        
        if sleep_length < gbl.MINIMUM_SLEEP_LENGTH:
            logger.info(
                    "sleep length %s is less than minimum of %s, turning on nightlight",
                    fmt(sleep_length), fmt(gbl.MINIMUM_SLEEP_LENGTH)
                    )
            await nightlight()
        else:
            logger.info(
                    "sleep length %s is greater than minimum of  %s, turning on light",
                    fmt(sleep_length), fmt(gbl.MINIMUM_SLEEP_LENGTH)
                    )
            await wake_up()

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

async def set_temp_on_switch():
    try:
        bulb = Bulb() # noqa: F841
    except Exception: # noqa: BLE001
        return

    # state = await bulb.updateState()
    # temp = state.get_temperature()
