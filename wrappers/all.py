import asyncio
import sys
from pathlib import Path
from typing import Optional

from utils.misc import mutable_globals
from wrappers.bulb_wrapper import Bulb
from wrappers.WLED_wrapper import WLED

sys.path.append(str(Path(__file__).parent))
from extra_types import RGBtype
from wrappers.base import WrapperBase


class AllObjects(WrapperBase):

    OBJECT_TYPE = "bulb" # type: ignore[reportAssignmentType]

    
    async def _turn_on(self, brightness: Optional[int], rgb: Optional[RGBtype]) -> None:
        async with asyncio.TaskGroup() as tg:
            if mutable_globals.use_bulb:
                tg.create_task(Bulb().turn_on(brightness = brightness, rgb = rgb))

            if mutable_globals.use_wled:
                tg.create_task(WLED().turn_on(brightness = brightness, rgb = rgb))

    async def _turn_off(self) -> None:
        async with asyncio.TaskGroup() as tg:
            if mutable_globals.use_bulb:
                tg.create_task(Bulb().turn_off())

            if mutable_globals.use_wled:
                tg.create_task(WLED().turn_off())
    
    async def toggle(self) -> None:
        async with asyncio.TaskGroup() as tg:
            if mutable_globals.use_bulb:
                tg.create_task(Bulb().toggle())

            if mutable_globals.use_wled:
                tg.create_task(WLED().toggle())

    @property
    async def is_on(self) -> bool:
        async with asyncio.TaskGroup() as tg:
            bulb_task = None
            wled_task = None

            if mutable_globals.use_bulb:
                bulb_task = tg.create_task(Bulb().is_on)

            if mutable_globals.use_wled:
                wled_task = tg.create_task(WLED().is_on)

        bulb_is_on = await bulb_task if bulb_task else False
        wled_is_on = await wled_task if wled_task else False

        return bulb_is_on and wled_is_on

    @property
    async def is_connected(self) -> bool:
        async with asyncio.TaskGroup() as tg:
            bulb_task = None
            wled_task = None

            if mutable_globals.use_bulb:
                bulb_task = tg.create_task(Bulb().is_connected)

            if mutable_globals.use_wled:
                wled_task = tg.create_task(WLED().is_connected)

        bulb_is_connected = await bulb_task if bulb_task else False
        wled_is_connected = await wled_task if wled_task else False

        return bulb_is_connected and wled_is_connected