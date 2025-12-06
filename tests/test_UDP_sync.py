import pytest

from UDP_sync import Colour, Effect, Nightlight, WLEDPacket


@pytest.fixture
def mock_packet() -> WLEDPacket:
    colour = Colour(red=255, green=100, blue=50, white=0)
    effect = Effect(index=2, speed=5, intensity=10, palette=1)
    nightlight = Nightlight(active=True, delay_mins=15)
    packet = WLEDPacket(_call_num=1,
                        brightness=200,
                        primary_color=colour,
                        secondary_color=colour,
                        effect=effect,
                        transition_duration_ms=500,
                        nightlight=nightlight,
                        _protocol_num=2
                        )
    return packet


def test_wled_packet_creation(mock_packet: WLEDPacket):
    assert mock_packet.brightness == 200
    assert mock_packet.primary_color.red == 255
    assert mock_packet.effect.index == 2
    assert mock_packet.nightlight.active is True
    assert mock_packet.call_mode == "1: Direct Change (UI/API)"
    assert mock_packet.protocol_version == "2: 0.4 (Secondary Color)"


def test_wled_packet_from_packet(mock_packet: WLEDPacket):
    data = bytearray(24)
    data[0] = 0  # packet purpose
    data[1] = mock_packet._call_num
    data[2] = mock_packet.brightness
    data[3] = mock_packet.primary_color.red
    data[4] = mock_packet.primary_color.green
    data[5] = mock_packet.primary_color.blue
    data[6] = int(mock_packet.nightlight.active)
    data[7] = mock_packet.nightlight.delay_mins
    data[8] = mock_packet.effect.index
    data[9] = mock_packet.effect.speed
    data[10] = mock_packet.primary_color.white
    data[11] = mock_packet._protocol_num
    data[12] = mock_packet.secondary_color.red
    data[13] = mock_packet.secondary_color.green
    data[14] = mock_packet.secondary_color.blue
    data[15] = mock_packet.secondary_color.white
    data[16] = mock_packet.effect.intensity
    data[17] = mock_packet.transition_duration_ms >> 8  # high byte
    data[18] = mock_packet.transition_duration_ms & 0xFF  # low byte
    data[19] = mock_packet.effect.palette

    decoded_packet = WLEDPacket.from_packet(data)
    assert decoded_packet == mock_packet

def test_dict_wled_packet(mock_packet: WLEDPacket):
    packet_dict = dict(mock_packet)
    expected = {
        "brightness": 200,
        "primary_color": {"red": 255, "green": 100, "blue": 50, "white": 0},
        "secondary_color": {"red": 255, "green": 100, "blue": 50, "white": 0},
        "nightlight": {"active": True, "delay_mins": 15}, 
        "effect": {"index": 2, "speed": 5, "intensity": 10, "palette": 1},
        "transition_duration_ms": 500,
        "call_mode": "1: Direct Change (UI/API)",
        "protocol_version": "2: 0.4 (Secondary Color)"
        }
    assert packet_dict == expected