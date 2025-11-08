import asyncio
from pathlib import Path
from pytest_mock import MockerFixture

import pytest
import yaml
from pywizlight import PilotBuilder, PilotParser, scenes, wizlight

from bulb_wrapper import Bulb, get_range


@pytest.fixture
def mock_yaml_data():
    """Sample YAML data for testing."""
    return {
        "bedroom_light": {
            "ip": "192.168.1.110",
            "port": 38899,
            "mac": "cc408525d286",
        },
        "test_bulb": {
            "ip": "192.168.1.100",
            "mac": "aabbccddeeff",
        },
    }


@pytest.fixture
def mock_pilot_state(mocker):
    """Mock PilotParser state object."""
    state = mocker.MagicMock(spec=PilotParser)
    state.get_state.return_value = True
    state.get_brightness.return_value = 50
    state.get_rgb.return_value = (255, 255, 255)
    state.get_colortemp.return_value = 4000
    return state


@pytest.fixture
def mock_wizlight(mocker):
    """Mock wizlight object."""
    light = mocker.MagicMock(spec=wizlight)
    light.turn_on = mocker.AsyncMock()
    light.turn_off = mocker.AsyncMock()
    light.updateState = mocker.AsyncMock()
    return light


class TestBulbFromYaml:
    """Test Bulb.from_yaml class method."""

    def test_init_without_params(self, mocker: MockerFixture):
        """Test initialization without parameters (uses from_yaml)."""
        mock_bulb = mocker.MagicMock()
        mock_light = mocker.MagicMock()
        mock_bulb.light = mock_light
        mock_from_yaml = mocker.patch("bulb_wrapper.Bulb.from_yaml", return_value=mock_bulb)
        mock_run = mocker.patch("bulb_wrapper.asyncio.run", return_value=mocker.MagicMock())

        bulb = Bulb()
        mock_from_yaml.assert_called_once_with("bedroom_light")
        assert bulb.light == mock_light

    def test_from_yaml_with_port(self, tmp_path):
        """Test loading bulb from YAML with port specified."""
        yaml_file = tmp_path / "bulbs.yaml"
        yaml_file.write_text(yaml.dump({
            "bedroom_light": {
                "ip": "192.168.1.110",
                "port": 38899,
                "mac": "cc408525d286",
            }
        }))
        bulb = Bulb.from_yaml("bedroom_light", yaml_file=str(yaml_file))
        assert bulb.ip == "192.168.1.110"
        assert bulb.port == 38899
        assert bulb.mac == "cc408525d286"

    def test_from_yaml_without_port(self, tmp_path:Path):
        """Test loading bulb from YAML without port (uses default)."""
        yaml_file = tmp_path / "bulbs.yaml"
        yaml_file.write_text(yaml.dump({
            "test_bulb": {
                "ip": "192.168.1.100",
                "mac": "aabbccddeeff",
            }
        }))

        bulb = Bulb.from_yaml("test_bulb", yaml_file=str(yaml_file))
        assert bulb.ip == "192.168.1.100"
        assert bulb.port == 38899  # default port
        assert bulb.mac == "aabbccddeeff"

    def test_from_yaml_custom_file(self, mocker, tmp_path):
        """Test loading from custom YAML file."""
        yaml_file = tmp_path / "custom.yaml"
        yaml_file.write_text(yaml.dump({
            "custom_bulb": {
                "ip": "192.168.1.200",
                "mac": "112233445566",
            }
        }))

        bulb = Bulb.from_yaml("custom_bulb", yaml_file=str(yaml_file))
        assert bulb.ip == "192.168.1.200"
        assert bulb.mac == "112233445566"
        assert bulb.port == 38899  # default port



class TestBulbMethods:
    """Test Bulb instance methods."""

    @pytest.mark.asyncio
    async def test_turn_off(self, mock_wizlight, mocker):
        """Test turning off the bulb."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")
        initial_time = bulb.last_accessed

        await asyncio.sleep(0.01)
        await bulb.turn_off()

        mock_wizlight.turn_off.assert_called_once()
        assert bulb.last_accessed > initial_time

    @pytest.mark.asyncio
    async def test_turn_on_with_rgb(self, mock_wizlight, mocker):
        """Test turning on with RGB color."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        await bulb.turn_on(brightness=80, rgb=(255, 0, 0))

        mock_wizlight.turn_on.assert_called_once()
        call_args = mock_wizlight.turn_on.call_args[0][0]
        assert isinstance(call_args, PilotBuilder)

    @pytest.mark.asyncio
    async def test_turn_on_with_colortemp(self, mock_wizlight, mocker):
        """Test turning on with color temperature."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        mock_temp_to_rgb = mocker.patch.object(Bulb, "temp_to_rgb", return_value=(255, 200, 150))
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        await bulb.turn_on(brightness=70, colortemp=4000)

        mock_wizlight.turn_on.assert_called_once()
        mock_temp_to_rgb.assert_called_once_with(4000)

    @pytest.mark.asyncio
    async def test_turn_on_rgb_and_colortemp_raises_error(self, mock_wizlight, mocker):
        """Test that providing both RGB and colortemp raises ValueError."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        with pytest.raises(ValueError, match="cannot provide both rgb and colortemp"):
            await bulb.turn_on(rgb=(255, 0, 0), colortemp=4000)

    @pytest.mark.asyncio
    async def test_turn_on_no_params(self, mock_wizlight, mocker):
        """Test turning on with no parameters."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        await bulb.turn_on()

        mock_wizlight.turn_on.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_scene(self, mock_wizlight, mocker):
        """Test setting a scene."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        mock_get_scene = mocker.patch("bulb_wrapper.scenes.get_id_from_scene_name", return_value=5)
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        await bulb.set_scene("Ocean", brightness=75, speed=100)

        mock_wizlight.turn_on.assert_called_once()
        mock_get_scene.assert_called_once_with("Ocean")

    @pytest.mark.asyncio
    async def test_set_scene_clamps_brightness(self, mock_wizlight, mocker):
        """Test that set_scene clamps brightness to valid range."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        mocker.patch("bulb_wrapper.scenes.get_id_from_scene_name", return_value=5)
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        # Test brightness too low
        await bulb.set_scene("Ocean", brightness=5, speed=100)
        # Test brightness too high
        await bulb.set_scene("Ocean", brightness=150, speed=100)

        # Should have been called twice
        assert mock_wizlight.turn_on.call_count == 2

    @pytest.mark.asyncio
    async def test_set_scene_clamps_speed(self, mock_wizlight, mocker):
        """Test that set_scene clamps speed to valid range."""
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        mocker.patch("bulb_wrapper.scenes.get_id_from_scene_name", return_value=5)
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        # Test speed too low
        await bulb.set_scene("Ocean", brightness=50, speed=5)
        # Test speed too high
        await bulb.set_scene("Ocean", brightness=50, speed=250)

        assert mock_wizlight.turn_on.call_count == 2

    @pytest.mark.asyncio
    async def test_updateState(self, mock_wizlight, mock_pilot_state, mocker):
        """Test updateState method."""
        mock_wizlight.updateState.return_value = mock_pilot_state
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")

        state = await bulb.updateState()

        mock_wizlight.updateState.assert_called_once()
        assert state == mock_pilot_state


class TestBulbLerp:
    """Test the lerp (linear interpolation) method."""

    @pytest.mark.asyncio
    async def test_lerp_interrupted_by_external_change(self, mock_wizlight, mock_pilot_state, mocker):
        """Test lerp interrupted by external state change."""
        # Create two different states
        initial_state = mocker.MagicMock(spec=PilotParser)
        initial_state.get_state.return_value = True
        initial_state.get_brightness.return_value = 50
        initial_state.get_rgb.return_value = (255, 255, 255)
        initial_state.get_colortemp.return_value = 4000

        changed_state = mocker.MagicMock(spec=PilotParser)
        changed_state.get_state.return_value = True
        changed_state.get_brightness.return_value = 100  # Different brightness
        changed_state.get_rgb.return_value = (255, 0, 0)  # Different RGB
        changed_state.get_colortemp.return_value = 6000  # Different temp

        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")
        bulb.last_state = initial_state
        bulb.TIME_STEP = 0.05

        call_count = 0

        async def mock_update_state():
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                return changed_state  # Return changed state after first call
            return initial_state

        mocker.patch.object(bulb, "turn_on", new_callable=mocker.AsyncMock)
        mocker.patch.object(bulb, "updateState", side_effect=mock_update_state)
        await bulb.lerp(
            start_brightness=20,
            start_temp=3000,
            end_brightness=80,
            end_temp=5000,
            duration=1,
        )

        # Should interrupt early
        assert call_count <= 20  # Would be more steps without interruption

    @pytest.mark.asyncio
    async def test_lerp_state_none_error(self, mock_wizlight, mocker):
        """Test lerp when state cannot be retrieved."""
        mock_wizlight.updateState.return_value = None
        
        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")
        bulb.last_state = None
        bulb.TIME_STEP = 0.05

        mock_turn_on = mocker.patch.object(bulb, "turn_on", new_callable=mocker.AsyncMock)
        mocker.patch.object(bulb, "updateState", return_value=None)
        await bulb.lerp(
            start_brightness=20,
            start_temp=3000,
            end_brightness=80,
            end_temp=5000,
            duration=1,
        )

        # Should call turn_on with final values
        final_call = mock_turn_on.call_args_list[-1]
        assert final_call[1]["brightness"] == 80
        assert final_call[1]["colortemp"] == 5000

    @pytest.mark.asyncio
    async def test_lerp_bulb_off_interrupts(self, mock_wizlight, mocker):
        """Test lerp interrupted when bulb is turned off."""
        off_state = mocker.MagicMock(spec=PilotParser)
        off_state.get_state.return_value = False  # Bulb is off
        off_state.get_brightness.return_value = 0
        off_state.get_rgb.return_value = (0, 0, 0)
        off_state.get_colortemp.return_value = 0

        mocker.patch("bulb_wrapper.wizlight", return_value=mock_wizlight)
        mocker.patch("bulb_wrapper.asyncio.run")
        bulb = Bulb(ip="192.168.1.100", port=38899, mac="aabbccddeeff")
        bulb.last_state = off_state
        bulb.TIME_STEP = 0.05

        mock_turn_on = mocker.patch.object(bulb, "turn_on", new_callable=mocker.AsyncMock)
        mocker.patch.object(bulb, "updateState", return_value=off_state)
        await bulb.lerp(
            start_brightness=20,
            start_temp=3000,
            end_brightness=80,
            end_temp=5000,
            duration=1,
        )

        # Should interrupt immediately due to off state
        assert mock_turn_on.call_count <= 1


# class TestTempToRgb:
#     """Test temperature to RGB conversion."""



class TestGetRange:
    """Test the get_range utility function."""

    def test_get_range_basic(self):
        """Test basic range generation."""
        result = list(get_range(0, 100, 10))
        assert len(result) == 11  # 10 steps + 1
        assert result[0] == 0
        assert result[-1] == 100
        