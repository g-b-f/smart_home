import utils
logger = utils.get_logger(__name__)

async def periodic_light_check():
    # a semi-abandoned idea that now functions more as a heartbeat
    zen = utils.get_zenith()
    logger.debug("Current zenith: %f", zen)
