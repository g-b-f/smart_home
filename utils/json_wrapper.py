import json
from datetime import datetime
from pathlib import Path
from typing import MutableMapping

from pydantic import ValidationError

from extra_types import MutableGlobals
from utils.get_logger import get_logger


# TODO: decouple from MutableGlobals
class JsonWrapper(MutableMapping):
    default = MutableGlobals.model_construct().model_dump()

    def __init__(self, file: Path):
        self.file = file
        self.logger = get_logger(file.stem)

    @staticmethod
    def _format_iso(obj):
        return obj.isoformat() if isinstance(obj, datetime) else obj

    def write_default(self):
        output = json.dumps(self.default, indent=4, default=self._format_iso)
        self.logger.info("writing default values:\n%s", output)
        self.file.write_text(output + "\n")
        
    @property
    def data(self) -> dict:
        try:
            ret = json.loads(self.file.read_text())
            MutableGlobals.model_validate(ret)
        except (FileNotFoundError, ValidationError) as e:
            self.logger.error("Error loading %s: %s. Reverting to default.", self.file.name, e)
            self.write_default()
            ret = self.default
        return ret

    @data.setter
    def data(self, d):
        self.file.write_text(json.dumps(d, indent=4, default=self._format_iso) + "\n")
    
    def _get_var(self, key:str):
        ret = self.data[key]
        self.logger.debug("%s is %s", key, ret)
        return ret
    
    def _set_var(self, key:str, val):
        data = self.data
        data[key] = val
        self.data = data

    @property
    def visitor_present(self) -> bool:
        return self._get_var("visitor_present")
    
    @visitor_present.setter
    def visitor_present(self, val:bool):
        self._set_var("visitor_present", val)

    @property
    def use_bulb(self) -> bool:
        return self._get_var("use_bulb")
    
    @use_bulb.setter
    def use_bulb(self, val:bool):
        self._set_var("use_bulb", val)
    
    @property
    def use_wled(self) -> bool:
        return False
        # return self._get_var("use_wled")
    
    @use_wled.setter
    def use_wled(self, val:bool):
        self._set_var("use_wled", val)

    @property
    def last_sleep(self) -> datetime:
        return datetime.fromisoformat(self._get_var("last_sleep"))
    
    @last_sleep.setter
    def last_sleep(self, val:datetime):
        self._set_var("last_sleep", val.isoformat())

    @property
    def auto_colourtemp(self) -> bool:
        return self._get_var("auto_colourtemp")

    @auto_colourtemp.setter
    def auto_colourtemp(self, val:bool):
        self._set_var("auto_colourtemp", val)

    def __getitem__(self, key):
        return self._get_var(key)
    
    def __setitem__(self, key, value):
        self._set_var(key, value)
    
    def __contains__(self, key):
        return key in self.data
    
    def __iter__(self):
        yield from self.data.items()

    def __len__(self):
        return len(self.data)
    
    def __repr__(self) -> str:
        return str(self.data)
    
    def __delitem__(self, key):
        data = self.data
        del data[key]
        self.data = data
        
