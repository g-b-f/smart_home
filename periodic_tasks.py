from utils.misc import get_logger, get_zenith, lerp_color_temp, mutable_globals
from wrappers.WLED_wrapper import WLED
from wrappers.bulb_wrapper import Bulb

logger = get_logger(__name__)

async def periodic_light_check():
    if not mutable_globals.auto_colourtemp:
        logger.debug("auto_colourtemp is disabled, skipping periodic light check")
        return
    
    zen = get_zenith()
    logger.debug("Current zenith: %f", zen)
    temp = lerp_color_temp(zen)
    logger.debug("Setting colourtemp to %d based on zenith", temp)

    if mutable_globals.use_wled:
        await WLED().turn_on(colortemp=temp)

    if mutable_globals.use_bulb:
        await Bulb().turn_on(colortemp=temp)
