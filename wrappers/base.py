from abc import ABCMeta, abstractmethod
import requests
from typing import Any, cast
from extra_types import WLEDResponse
from utils import get_logger

class WrapperBase(metaclass=ABCMeta):