import asyncio
import sys
from pathlib import Path

import pytest
import yaml
from pytest_mock import MockerFixture
from pywizlight import PilotBuilder, PilotParser, wizlight

sys.path.append(str(Path(__file__).parent))

from wrappers.bulb_wrapper import Bulb, get_range

def test_change_globals_from_cli():
    pass