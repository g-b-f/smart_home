from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Callable, Mapping

import astral.sun
import humanize

import global_vars as gbl
from extra_types import WayPointType
from utils.get_logger import get_logger
from utils.json_wrapper import MutableGlobalsWrapper

logger = get_logger(__name__)

mutable_globals = MutableGlobalsWrapper(Path(__file__).parent / "mutable_globals.json")

def format_time(t: datetime| timedelta | time) -> str:
    if isinstance(t, timedelta):
        return humanize.precisedelta(t)
    elif isinstance(t, datetime):
        return t.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(t, time):
        return t.strftime("%H:%M:%S")

    else:
        raise ValueError("Input must be a datetime, timedelta, or time object")


def config_to_bool_function(option: str|bool|int) -> Callable[[bool, str], bool]:
    toggle = ["toggle", "t"]
    true = ["true", True, 1, "1"]
    false = ["false", False, 0, "0"]
    option = option.lower() if isinstance(option, str) else option

    functions = {
        **dict.fromkeys(toggle, lambda x: not x), 
        **dict.fromkeys(true, lambda x: True),
        **dict.fromkeys(false, lambda x: False)
    } # type: ignore[misc]
    
    if option not in functions:
        raise ValueError(f"Invalid option: {option}")
    
    def func(current_value:bool, name:str) -> bool:
        new_value = functions[option](current_value)
        logger.info("%s was %s, now %s", name, current_value, new_value)
        return new_value
    
    return func

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def get_zenith(location = astral.LocationInfo()) -> float:
    return astral.sun.zenith(location.observer)


def lerp_color_temp(waypoint: WayPointType, waypoints_dict: Mapping[WayPointType, int]) -> int:
    """Linearly interpolates the colourtemp for a given input based on a dictionary of waypoints.

    Args:
        waypoint: The input
        waypoints_dict: A dictionary where keys are the input values and values are the corresponding colourtemp.

    Returns:
        int: The desired colourtemp for the input
    """
    waypoints = sorted(waypoints_dict.items(), key=lambda item: item[0])

    if waypoint <= waypoints[0][0]:
        return waypoints[0][1]
    if waypoint >= waypoints[-1][0]:
        return waypoints[-1][1]

    for i in range(len(waypoints) - 1):
        waypoint_1, colortemp_1 = waypoints[i]
        waypoint_2, colortemp_2 = waypoints[i + 1]

        if waypoint_1 <= waypoint <= waypoint_2:
            factor = (waypoint - waypoint_1) / (waypoint_2 - waypoint_1)
            return round(colortemp_1 + factor * (colortemp_2 - colortemp_1))
    
    raise RuntimeError("couldn't get colourtemp. There might be something wrong with the waypoints dict")


def smoothstep_color_temp(waypoint: WayPointType, waypoints_dict: Mapping[WayPointType, int]) -> int:
    """Interpolates the colourtemp for a given input using an ease-in-out curve.

    Args:
        waypoint: The input
        waypoints_dict: A dictionary where keys are the input values and values are the corresponding colourtemp.

    Returns:
        int: The desired colourtemp for the input
    """
    waypoints = sorted(waypoints_dict.items(), key=lambda item: item[0])

    if waypoint <= waypoints[0][0]:
        return waypoints[0][1]
    if waypoint >= waypoints[-1][0]:
        return waypoints[-1][1]

    for i in range(len(waypoints) - 1):
        waypoint_1, colortemp_1 = waypoints[i]
        waypoint_2, colortemp_2 = waypoints[i + 1]

        if waypoint_1 <= waypoint <= waypoint_2:
            linear_factor = (waypoint - waypoint_1) / (waypoint_2 - waypoint_1)
            eased_factor = linear_factor * linear_factor * (3.0 - 2.0 * linear_factor)
            return round(colortemp_1 + eased_factor * (colortemp_2 - colortemp_1))
    
    raise RuntimeError("couldn't get colourtemp. There might be something wrong with the waypoints dict")


def legacy_get_colourtemp_for_time(waypoint: int, d:dict) -> int:
    location = astral.LocationInfo()
    date=None
    sun = Sun(location, date)

    t = time(hour=waypoint // 3600, minute=(waypoint % 3600) // 60, second=waypoint % 60)
    now = datetime.combine(astral.now(location.tzinfo).date(), t).replace(tzinfo=sun.location.tzinfo)


    if now < sun.dawn or now > sun.dusk:
        return gbl.NIGHT_COLOURTEMP
    elif sun.dawn <= now < sun.sunrise:
        return gbl.SUNRISE_COLOURTEMP
    elif sun.sunrise <= now < sun.sunset:
        return gbl.DAY_COLOURTEMP
    elif sun.sunset <= now < sun.dusk:
        return gbl.SUNSET_COLOURTEMP
    else:
        return gbl.SUNSET_COLOURTEMP


def colourtemp_from_zenith(z: float|None = None) -> int:
    zen = z or get_zenith()
    waypoints = gbl.ZENITH_WAYPOINTS
    return lerp_color_temp(zen, waypoints)


def _time_to_seconds(t: time) -> int:
    """Converts a datetime.time object into total seconds since midnight."""
    return t.hour * 3600 + t.minute * 60 + t.second

InterpolateFuncType = Callable[[WayPointType, Mapping[WayPointType, int]], int]
def colourtemp_from_time(t: time | None = None, func: InterpolateFuncType = lerp_color_temp) -> int:
    time_input = t or datetime.now().time()
    seconds_now = _time_to_seconds(time_input)

    waypoints = gbl.TIME_WAYPOINTS.items()
    seconds_waypoints = { _time_to_seconds(t): temp for t, temp in waypoints }
    return func(seconds_now, seconds_waypoints)


class Sun:
    def __init__(self, location = astral.LocationInfo(), date=None):
        self.location = location
        if date is None:
            self.date = astral.today(location.tzinfo)
        self.sun = astral.sun.sun(location.observer, date, tzinfo=location.tzinfo)

    def __getattribute__(self, name: str):
        if name in {"dawn", "sunrise", "noon", "sunset", "dusk"}:
            return self.sun[name]
        return super().__getattribute__(name)

    def __repr__(self):
        return f"Sun({self.location}): {self.sun}"


if __name__ == "__main__":
    mutable_globals.write_default()
