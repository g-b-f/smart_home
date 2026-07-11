from utils.get_logger import get_logger
from utils.misc import colourtemp_from_zenith, colourtemp_from_time, mutable_globals
from wrappers.all import AllObjects

logger = get_logger(__name__)

async def periodic_light_check():
    if not mutable_globals.auto_colourtemp:
        logger.debug("auto_colourtemp is disabled, skipping periodic light check")
        return

    if mutable_globals.zenith_not_time:
        temp = colourtemp_from_zenith()
        logger.debug("Setting colourtemp to %d based on zenith", temp)
    else:
        temp = colourtemp_from_time()
        logger.debug("Setting colourtemp to %d based on time", temp)
    await AllObjects().turn_on(colortemp=temp)