import asyncio
import bellows.zigbee.application

class ZigbeeNetworkListener:
    """Listener for Zigbee network events such as device joins and initialization."""

    def device_joined(self, network_device):
        print(f"Device joined: {network_device.ieee}")

    def device_initialized(self, network_device):
        print(f"Device initialized: {network_device.ieee}")
        print(f"Manufacturer: {network_device.manufacturer}")
        print(f"Model: {network_device.model}")

    def device_left(self, network_device):
        print(f"Device left: {network_device.ieee}")

async def permit_device_pairing(serial_port_path: str, permit_duration_seconds: int = 120):
    """Opens the Zigbee network for pairing and listens for joining devices.

    Args:
        serial_port_path: The file path to the Zigbee adapter serial device.
        permit_duration_seconds: How long the coordinator should allow joins.
    """
    coordinator_configuration = {
        "device": {
            "path": serial_port_path
        },
        "database_path": "zigbee_network.db"
    }

    coordinator_application = await bellows.zigbee.application.ControllerApplication.new(
        config=coordinator_configuration,
        auto_form=True
    )

    network_listener = ZigbeeNetworkListener()
    coordinator_application.add_listener(network_listener)

    await coordinator_application.permit(permit_duration_seconds)
    print(f"Network open for pairing for {permit_duration_seconds} seconds. Put device in pairing mode.")

    await asyncio.sleep(permit_duration_seconds)
    print("Pairing window closed.")

if __name__ == "__main__":
    asyncio.run(permit_device_pairing("/dev/ttyUSB0"))
