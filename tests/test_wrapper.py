import asyncio
import sys
from pathlib import Path

import pytest
import yaml
from pytest_mock import MockerFixture
from pywizlight import PilotBuilder, PilotParser, wizlight

sys.path.append(str(Path(__file__).parent))

from wrappers.bulb_wrapper import Bulb
from wrappers.WLED_wrapper import WLED

from wrappers.base import FailedConnectionError, ignore_failed_connection

def test_ignore_exception_annotation(mocker: MockerFixture):
    class TestClass:
        logger = mocker.Mock()

        async def test_method_should_raise(self):
            raise FailedConnectionError
        
        @ignore_failed_connection
        async def test_method_should_not_raise(self):
            raise FailedConnectionError
        
    test_instance = TestClass()

    with pytest.raises(FailedConnectionError):
        asyncio.run(test_instance.test_method_should_raise())
    asyncio.run(test_instance.test_method_should_not_raise())