
import math
from typing import cast

from extra_types import RGBtype
from utils.misc import clamp


def rgb_to_hex(rgb: RGBtype) -> str:
    return "{:02X}{:02X}{:02X}".format(*rgb)


def hex_to_rgb(hex_colour: str) -> RGBtype:
    hex_colour = hex_colour.lstrip('#')
    if len(hex_colour) == 3:
        hex_colour = ''.join([c*2 for c in hex_colour])
    if len(hex_colour) != 6:
        raise ValueError("Hex color must be in the format RRGGBB or RGB")
    r = int(hex_colour[0:2], 16)
    g = int(hex_colour[2:4], 16)
    b = int(hex_colour[4:6], 16)
    return (r, g, b)


def temp_to_rgb(temp: int|float) -> RGBtype:
    """Convert color temperature in Kelvin to RGB values.

    input colourtemp should be between 1000 and 40000 Kelvin

    Algorithm from Tanner Helland (http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/)
    """
    temp = cast(float, temp / 100)

    if temp <= 66:
        red = 255.0
        green = temp
        green = 99.4708025861 * math.log(green) - 161.1195681661
        if temp <= 19:
            blue = 0.0
        else:
            blue = temp - 10.0
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
    else:
        red = temp - 60
        red = 329.698727446 * (red ** -0.1332047592)
        green = temp - 60
        green = 288.1221695283 * (green ** -0.0755148492)
        blue = 255.0

    red = clamp(red, 0.0, 255.0)
    green = clamp(green, 0.0, 255.0)
    blue = clamp(blue, 0.0, 255.0)

    return round(red), round(green), round(blue)  

def rgb_to_temp(rgb_or_hex: RGBtype | str, approximate=True) -> int:
    """The reverse of `temp_to_rgb`.
    Brute forces the answer because I don't want to manually calculate it

    Args:
        rgb_or_hex (RGBtype | str): The color, as either an (r,g,b) tuple or hex string
        approximate (bool, optional): Whether to get an approximation using euclidean distance. Defaults to True.

    Raises:
        RuntimeError: If a temperature couldn't be found.

    Returns:
        int: the colour temperature that matches the input value
    """
    rgb_target = hex_to_rgb(rgb_or_hex) if isinstance(rgb_or_hex, str) else rgb_or_hex

    best_dist = 100.0 # any further than this gives dubious results 
    best_temp = None
    for temp in range(1_000, 10_000):
        rgb_current = temp_to_rgb(temp)
        if rgb_current == rgb_target:
            return temp

        if not approximate:
            continue

        dist = math.dist(rgb_current, rgb_target)
        if dist < best_dist:
            best_dist = dist
            best_temp = temp

    if best_temp is not None:
        return best_temp
    else:
        raise RuntimeError(f"couldn't get temp for {rgb_or_hex}")
