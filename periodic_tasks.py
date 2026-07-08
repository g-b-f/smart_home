from utils.misc import get_logger, get_zenith, lerp_color_temp, mutable_globals

logger = get_logger(__name__)

async def periodic_light_check():
    if not mutable_globals.auto_colourtemp:
        logger.debug("auto_colourtemp is disabled, skipping periodic light check")
        return
    
    zen = get_zenith()
    logger.debug("Current zenith: %f", zen)
    temp = lerp_color_temp(zen)
