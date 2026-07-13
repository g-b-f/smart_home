import asyncio
import time

from pywizlight import (  # type: ignore[import-untyped]
    PilotBuilder,
)

import lighting_routines as Routine
from utils.get_logger import get_logger
from wrappers.bulb_wrapper import Bulb

logger = get_logger(__name__, level="debug")

async def tester():
    logger.info("tracking start")
    await Routine.tracking_start()

    logger.info("sleeping")
    time.sleep(3)

    logger.info("tracking stopped")
    await Routine.tracking_stopped()

async def tester2():
    bulb = Bulb()
    light = bulb.light

    # print(await light.getBulbConfig())
    # print(await light.getModelConfig())
    # print(await light.getUserConfig())
    # print(await light.get_bulbtype())

    builder = PilotBuilder(rgbww=(0, 0, 0, 0, 255))

    await light.turn_on(builder)


asyncio.run(tester2())