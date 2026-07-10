from utils.misc import colourtemp_from_zenith, get_logger, mutable_globals
from wrappers.bulb_wrapper import Bulb
from wrappers.WLED_wrapper import WLED

logger = get_logger(__name__)

async def periodic_light_check():
    if not mutable_globals.auto_colourtemp:
        logger.debug("auto_colourtemp is disabled, skipping periodic light check")
        return
    
    temp = colourtemp_from_zenith()
    logger.debug("Setting colourtemp to %d based on zenith", temp)

    if mutable_globals.use_wled:
        await WLED().turn_on(colortemp=temp)

    if mutable_globals.use_bulb:
        await Bulb().turn_on(colortemp=temp)
