import utils
logger = utils.get_logger(__name__)

async def periodic_light_check():
    zen = utils.get_zenith()
    logger.debug("Current zenith: %f", zen)
