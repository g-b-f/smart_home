import json
import socket
from dataclasses import dataclass

from utils import get_logger

logger = get_logger(__name__)

PORT = 21324
BUFFER_SIZE = 2**12

CALL_MODE_NAMES = {
    0: "Initial Boot",
    1: "Direct Change (UI/API)",
    2: "Button Press",
    3: "Notification Update",
    4: "Nightlight Activated",
    5: "Other",
    6: "Effect Changed",
    7: "Hue Light Changed",
    8: "Preset Cycle",
    9: "Blynk Update",
}

PROTOCOL_VERSION_NAMES = {
    0: "0.3 (Basic)",
    1: "0.4p (White)",
    2: "0.4 (Secondary Color)",
    3: "0.5.0 (Effect Intensity)",
    4: "0.6.0 (Transition Time)",
    5: "0.8.0 (Palettes)",
}

class Packet:
    def __iter__(self):
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, Packet):
                v = dict(v)
            yield k, v

@dataclass
class Colour(Packet):
    red: int
    green: int
    blue: int
    white: int = 0
    
@dataclass
class Effect(Packet):
    index: int
    speed: int
    intensity: int
    palette: int

@dataclass
class Nightlight(Packet):
    active: bool
    delay_mins: int

@dataclass
class WLEDPacket(Packet):
    _call_num: int
    brightness: int
    primary_color: Colour
    secondary_color: Colour
    nightlight: Nightlight
    effect: Effect
    transition_duration_ms: int
    _protocol_num: int

    def __post_init__(self):
        self.call_mode = f"{self._call_num}: {CALL_MODE_NAMES.get(self._call_num, 'Unknown')}"
        self.protocol_version = f"{self._protocol_num}: {PROTOCOL_VERSION_NAMES.get(self._protocol_num, 'Unknown')}"

    @classmethod
    def from_packet(cls, data) -> 'WLEDPacket':
        if len(data) < 24:
            raise ValueError("Packet too short")
        
        packet_purpose = data[0]
        if packet_purpose != 0:
            raise ValueError("Not a WLED notifier packet")
        
        call_mode = data[1]
        brightness = data[2]
        primary_red = data[3]
        primary_green = data[4]
        primary_blue = data[5]
        nightlight_active = data[6]
        nightlight_delay = data[7]
        effect_index = data[8]
        effect_speed = data[9]
        primary_white = data[10]
        protocol_version = data[11]
        secondary_red = data[12]
        secondary_green = data[13]
        secondary_blue = data[14]
        secondary_white = data[15]
        effect_intensity = data[16]
        transition_hi = data[17]
        transition_lo = data[18]
        effect_palette = data[19]
        transition_duration = (transition_hi << 8) | transition_lo

        return WLEDPacket(
            _call_num=call_mode,
            brightness=brightness,
            primary_color=Colour(primary_red, primary_green, primary_blue, primary_white),
            secondary_color=Colour(secondary_red, secondary_green, secondary_blue, secondary_white),
            nightlight=Nightlight(bool(nightlight_active), nightlight_delay),
            effect=Effect(effect_index, effect_speed, effect_intensity, effect_palette),
            transition_duration_ms=transition_duration,
            _protocol_num=protocol_version
        )        

def listen_udp():
    """Listen for UDP messages on the specified port and log them."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))
    
    logger.info("WLED UDP listener started on port %d", PORT)
    
    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            decoded = WLEDPacket.from_packet(data)
            logger.info("Received from %s:%d", addr[0], addr[1])
            logger.info(json.dumps(dict(decoded), indent=2))
                
    except KeyboardInterrupt:
        logger.info("UDP listener stopped")
    finally:
        sock.close()


if __name__ == "__main__":
    listen_udp()
