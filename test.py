from lighting_routines import Routine
import logging
import asyncio
logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S", format="%(asctime)s %(name)s - %(message)s")
logging.info("waking up")
asyncio.run(Routine.wake_up())