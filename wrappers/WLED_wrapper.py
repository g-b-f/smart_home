import asyncio
from typing import cast

import requests

from extra_types import RGBtype, WLEDResponse
from utils import get_logger
from wrappers.base import WrapperBase

TOGGLE = "t"

class WLED(WrapperBase):
    logger = get_logger(__name__, "INFO")

    def __init__(self, ip="192.168.1.121", **kwargs):
        self.url = f"http//{ip.rstrip('/')}/json/"
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
        return cast(WLEDResponse, self._get())

    @property
    async def is_on(self) -> bool:
        state = self.info.get("state", {})
        return state.get("on", False)
    
    async def turn_on(self):
        self._set(on=True)
    
    async def turn_off(self):
        try:
            self._set(on=False)
        except Exception as e:
            self.logger.error("couldn't turn off WLED: %s", e)
        
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
            self.colour = list(colour)

    @property
    def colour(self) -> list:
        seg = self._get_seg()
        return seg["col"]
    
    @colour.setter
    def colour(self, colours: list[int] | list[list[int]]):
        if all(isinstance(c, int) for c in colours):
            self._set_seg(col=[colours])
        elif all(isinstance(c, list) for c in colours):
            self._set_seg(col=colours)
        else:
            raise ValueError("Colours must be a list of integers or a list of list of integers")



# print(LedStrip.toggle())

if __name__ == "__main__":
    LedStrip = WLED()
    # print(LedStrip.info)
    # print(LedStrip.is_on)
    # LedStrip.set_solid()
    # LedStrip.set_effect(1)
    asyncio.run(LedStrip.turn_on())
