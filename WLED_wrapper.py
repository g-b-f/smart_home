import requests
from typing import Any, cast
from extra_types import WLEDResponse
from utils import get_logger
TOGGLE = "t"

class WLED:
    logger = get_logger(__name__, "DEBUG")

    def __init__(self, ip="http://192.168.1.121"):
        self.url = ip.rstrip('/') + '/json/'
        self._session = requests.Session()
        self._session.headers.update({'Content-Type': 'application/json'})

        self._effects = self.info["effects"]

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
    def info(self) -> WLEDResponse:
        return cast(WLEDResponse, self._get())

    @property
    def is_on(self) -> bool:
        state = self.info.get("state", {})
        return state.get("on", False)
    
    def toggle(self):
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
                self.logger.error(f"Effect '{effect}' not found")
                return
        else:
            effect_index = effect
        self._set_seg(fx=effect_index)
    
    def set_solid(self):
        self.set_effect("Solid")

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

LedStrip = WLED()

# print(LedStrip.toggle())

if __name__ == "__main__":
    # print(LedStrip.info)
    # print(LedStrip.is_on)
    # LedStrip.set_solid()
    LedStrip.set_effect(1)