import asyncio
import time

import lighting_routines as Routine
from utils.misc import get_logger

logger = get_logger(__name__, level="debug")

async def tester():
    logger.info("tracking start")
    await Routine.tracking_start()

    logger.info("sleeping")
    time.sleep(3)

    logger.info("tracking stopped")
    await Routine.tracking_stopped()

asyncio.run(tester())