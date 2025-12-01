import socket
from utils import get_logger

logger = get_logger(__name__, "DEBUG")

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


def decode_wled_packet(data):
    """Decode a WLED UDP notifier packet."""
    if len(data) < 24:
        return {"error": "Packet too short", "raw_length": len(data)}
    
    packet_purpose = data[0]
    
    # Check if this is a WLED notifier packet (byte 0 should be 0)
    if packet_purpose != 0:
        return {
            "type": "UDP Realtime Protocol",
            "packet_purpose": packet_purpose,
            "note": "Not a WLED notifier packet"
        }
    
    # Decode WLED notifier packet
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
    
    return {
        "type": "WLED Notifier",
        "call_mode": f"{call_mode} ({CALL_MODE_NAMES.get(call_mode, 'Unknown')})",
        "brightness": brightness,
        "primary_color": f"RGB({primary_red},{primary_green},{primary_blue}) W:{primary_white}",
        "secondary_color": f"RGB({secondary_red},{secondary_green},{secondary_blue}) W:{secondary_white}",
        "nightlight": {
            "active": bool(nightlight_active),
            "delay_mins": nightlight_delay
        },
        "effect": {
            "index": effect_index,
            "speed": effect_speed,
            "intensity": effect_intensity,
            "palette": effect_palette
        },
        "transition_duration_ms": transition_duration,
        "protocol_version": f"{protocol_version} ({PROTOCOL_VERSION_NAMES.get(protocol_version, 'Unknown')})",
    }


def listen_udp():
    """Listen for UDP messages on the specified port and log them."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))
    
    logger.info(f"WLED UDP listener started on port {PORT}")
    
    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            decoded = decode_wled_packet(data)
            logger.info(f"Received from {addr[0]}:{addr[1]}")
            
            if decoded.get("type") == "WLED Notifier":
                logger.info(f"  Type: WLED Notifier")
                logger.info(f"  Call Mode: {decoded['call_mode']}")
                logger.info(f"  Brightness: {decoded['brightness']}")
                logger.info(f"  Primary: {decoded['primary_color']}")
                logger.info(f"  Secondary: {decoded['secondary_color']}")
                logger.info(f"  Effect: index={decoded['effect']['index']} "
                          f"speed={decoded['effect']['speed']} "
                          f"intensity={decoded['effect']['intensity']} "
                          f"palette={decoded['effect']['palette']}")
                logger.info(f"  Nightlight: active={decoded['nightlight']['active']} "
                          f"delay={decoded['nightlight']['delay_mins']}min")
                logger.info(f"  Transition: {decoded['transition_duration_ms']}ms")
                logger.info(f"  Protocol: {decoded['protocol_version']}")
            else:
                logger.info(f"  {decoded}")
                logger.info(f"  Raw bytes ({len(data)}): {data.hex()}")
                
    except KeyboardInterrupt:
        logger.info("UDP listener stopped")
    finally:
        sock.close()


if __name__ == "__main__":
    listen_udp()