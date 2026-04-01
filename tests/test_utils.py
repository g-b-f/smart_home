from datetime import datetime, timedelta
from pathlib import Path

import pytest
from pytest import LogCaptureFixture

from utils import JsonWrapper, config_to_bool_function


@pytest.fixture
def wrapper(tmp_path:Path):
    fpath = tmp_path / "output.json"
    fpath.touch()
    return JsonWrapper(fpath)

def check_defaults(wrapper: JsonWrapper):
    assert not wrapper.visitor_present
    assert wrapper.use_bulb
    assert wrapper.use_wled
    # last_sleep should initialise to datetime.now(), but we give some leeway:
    assert datetime.now() - wrapper.last_sleep < timedelta(seconds=5)

class TestMutableGlobals:
    def test_write_default(self, wrapper: JsonWrapper):
        assert not wrapper.file.read_text()
        wrapper.write_default()
        check_defaults(wrapper)


    def test_write_vars(self, wrapper: JsonWrapper):
        wrapper.write_default()
        check_defaults(wrapper)

        wrapper.visitor_present = True
        wrapper.use_bulb = False
        wrapper.use_wled = False
        wrapper.last_sleep = datetime(2024, 1, 1, 12, 0, 0)

        assert wrapper.visitor_present
        assert not wrapper.use_bulb
        assert not wrapper.use_wled
        assert wrapper.last_sleep == datetime(2024, 1, 1, 12, 0, 0)

    def test_read_error_writes_default(self, wrapper: JsonWrapper, caplog:LogCaptureFixture):
        wrapper.write_default()
        check_defaults(wrapper)

        wrapper.visitor_present = 1234 # type: ignore[assignment]
        wrapper.data
        check_defaults(wrapper)

        for record in caplog.records:
            if record.levelname == "ERROR" and "Error loading" in record.message:
                return
        raise AssertionError("Expected error log not found")
    
class TestConfigToBoolFunction:
    @pytest.mark.parametrize("option", ["true", "True", True, 1, "1"])
    def test_set_true(self, option):
        func = config_to_bool_function(option)
        assert func(True, "")
        assert func(False, "")
    
    @pytest.mark.parametrize("option", ["false", "False", False, 0, "0"])
    def test_set_false(self, option):
        func = config_to_bool_function(option)
        assert not func(True, "")
        assert not func(False, "")

    @pytest.mark.parametrize("option", ["toggle", "Toggle", "t", "T"])
    def test_toggle(self, option):
        func = config_to_bool_function(option)
        assert not func(True, "")
        assert func(False, "")

    def test_invalid_option(self):
        with pytest.raises(ValueError):
            config_to_bool_function("qwerty")

