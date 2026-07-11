from datetime import datetime
from typing import Any, Literal, Protocol, TypedDict, TypeVar

from pydantic import BaseModel, Field


class WayPointProtocol(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...
    def __le__(self, other: Any, /) -> bool: ...
    def __gt__(self, other: Any, /) -> bool: ...
    def __ge__(self, other: Any, /) -> bool: ...
    def __eq__(self, other: Any, /) -> bool: ...
    def __sub__(self, other: Any, /) -> Any: ...
    def __add__(self, other: Any, /) -> Any: ...

WayPointType = TypeVar("WayPointType", bound=WayPointProtocol)


class MutableGlobals(BaseModel):
    visitor_present: bool = Field(default=False, description="Whether a visitor is currently present")
    use_bulb: bool = Field(default=True, description="Whether to connect to the lightbulb")
    use_wled: bool = Field(default=True, description="Whether to connect to the WLED strip")
    auto_colourtemp: bool = Field(default=True, description="Whether to adjust the colourtemp based on time of day")
    zenith_not_time: bool = Field(default=False, description="Whether to use zenith instead of time for colourtemp adjustment")
    last_sleep: datetime = Field(default_factory=datetime.now, description="The last time sleep tracking was active")

RGBtype = tuple[int, int, int]
RGBWtype = tuple[int, int, int, int]

SceneType = Literal[
    "Alarm",
    "Bedtime",
    "Candlelight",
    "Christmas",
    "Cozy",
    "Cool white",
    "Daylight",
    "Diwali",
    "Deep dive",
    "Fall",
    "Fireplace",
    "Forest",
    "Focus",
    "Golden white",
    "Halloween",
    "Jungle",
    "Mojito",
    "Night light",
    "Ocean",
    "Party",
    "Pulse",
    "Pastel colors",
    "Plantgrowth",
    "Romance",
    "Relax",
    "Sunset",
    "Spring",
    "Summer",
    "Steampunk",
    "True colors",
    "TV time",
    "White",
    "Wake-up",
    "Warm white",
    "Rhythm",
]



class Nightlight(TypedDict):
    on: bool
    dur: int
    fade: bool
    tbri: int

class UDPn(TypedDict):
    send: bool
    recv: bool

class Segment(TypedDict):
    start: int
    stop: int
    len: int
    col: list[RGBtype | RGBWtype]
    fx: int
    sx: int
    ix: int
    pal: int
    sel: bool
    rev: bool
    cln: int

class State(TypedDict):
    on: bool
    bri: int
    transition: int
    ps: int
    pl: int
    nl: Nightlight
    udpn: UDPn
    seg: list[Segment]

class LEDs(TypedDict):
    count: int
    rgbw: bool
    pin: list[int]
    pwr: int
    maxpwr: int
    maxseg: int

class Info(TypedDict):
    ver: str
    vid: int
    leds: LEDs
    name: str
    udpport: int
    live: bool
    fxcount: int
    palcount: int
    arch: str
    core: str
    freeheap: int
    uptime: int
    opt: int
    brand: str
    product: str
    btype: str
    mac: str

class WLEDResponse(TypedDict):
    state: State
    info: Info
    effects: list[str]
    palettes: list[str]
