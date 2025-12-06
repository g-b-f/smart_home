import asyncio
from typing import cast, Optional

import requests

from extra_types import RGBtype, WLEDResponse
from utils import get_logger, clamp
from wrappers.base import WrapperBase

TOGGLE = "t"

class WLED(WrapperBase):
    STRIP_NAME = "fairy_lights"
    logger = get_logger(__name__, "INFO") # type: ignore[reportAssignmentType]
    OBJECT_TYPE = "WLED" # type: ignore[reportAssignmentType]

    def __init__(self, ip:Optional[str]=None, **kwargs):
        if ip is None:
            self.url = self.from_yaml(self.STRIP_NAME).url
        else:
            self.url = f"http://{ip.rstrip('/')}/json/"

        self._session = requests.Session()
        self._session.headers.update({'Content-Type': 'application/json'})

        info = self.info
        self._effects = info["effects"]

        try:
            if "mac" in kwargs:
                expected_mac = kwargs["mac"]
                assert isinstance(expected_mac, str), "MAC address must be a string"
                expected_mac = expected_mac.lower().replace(":", "")
                actual_mac = info["info"]["mac"].lower().replace(":", "")
                if expected_mac != actual_mac:
                    self.logger.warning("MAC address mismatch: expected %s but got %s", expected_mac, actual_mac)
        except KeyError as e:
            self.logger.error("Couldn't verify MAC address; '%s' field missing in WLED response", e)


    def _request(self, method:str, endpoint="", **kwargs) -> dict:
        if method.lower() not in {"get", "post"}:
            raise ValueError("Unsupported HTTP method")
        result = self._session.request(method, self.url + endpoint.lstrip('/'), **kwargs)
        result.raise_for_status()
        return result.json()
    
    def _get(self, endpoint="") -> dict:
        return self._request("get", endpoint)
    
    def _post(self, endpoint="", json_data=None) -> dict:
        return self._request("post", endpoint, json=json_data)
    
    def _set(self, **kwargs):
        self._post("", json_data=kwargs)

    @property
    def config(self) -> dict:
        return self._get("cfg")

    @property
    def info(self) -> WLEDResponse:
        try:
            return cast(WLEDResponse, self._get())
        except Exception as e:
            self.logger.error("couldn't get info")
            return {}

    @property
    async def is_on(self) -> bool:
        state = self.info.get("state", {})
        return state.get("on", False)
    
    async def _turn_on(self, brightness: Optional[int] = None, rgb: Optional[RGBtype] = None):
        if rgb is not None:
            self.colour = rgb
        if brightness is not None:
            self.brightness = brightness
        self._set(on=True)
    
    async def _turn_off(self):
        self._set(on=False)
        
    async def toggle(self): 
        self._set(on=TOGGLE)

    def _set_seg(self, **kwargs):
        self._set(seg= [kwargs])

    def _get_seg(self):
        return self.info["state"]["seg"][0]
    
    def set_effect(self, effect: int | str):
        if isinstance(effect, str):
            try:
                effect_index = self._effects.index(effect)
            except ValueError:
                self.logger.error("Effect '%s' not found", effect)
                return
        else:
            effect_index = effect
        self._set_seg(fx=effect_index)

    
    def set_solid(self, colour: RGBtype | None = None):
        self.set_effect("Solid")
        if colour is not None:
            self.colour = colour

    @property
    def colour(self) -> list:
        seg = self._get_seg()
        return seg["col"]
    
    @colour.setter
    def colour(self, colours: RGBtype | list[RGBtype]):
        if all(isinstance(c, int) for c in colours):
            self._set_seg(col=[colours])
        elif all(isinstance(c, list) for c in colours):
            self._set_seg(col=colours)
        else:
            raise ValueError("Colours must be a list of integers or a list of list of integers")
        
    @property
    def brightness(self) -> int:
        return self.info["state"]["bri"]
    
    @brightness.setter
    def brightness(self, value: int):
        value = self.clamp_brightness(value)
        self._set(bri=value)

    def clamp_brightness(self, value: int) -> int:
        """Clamp brightness value between 0 and 255."""
        return clamp(value, 0, 255)
    
    async def get_info(self):
        return self.info


if __name__ == "__main__":
    LedStrip = WLED()
    # print(LedStrip.info)
    # print(LedStrip.is_on)
    # LedStrip.set_solid()
    # LedStrip.set_effect(1)
    asyncio.run(LedStrip.turn_on())
