from utils.misc import get_logger, get_zenith

logger = get_logger(__name__)

async def periodic_light_check():
    # a semi-abandoned idea that now functions more as a heartbeat
    zen = get_zenith()
    logger.debug("Current zenith: %f", zen)
