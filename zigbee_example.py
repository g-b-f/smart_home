import asyncio
from pathlib import Path
import sys
import bellows.zigbee.application
from bellows.zigbee.application import ControllerApplication
import zigpy.application
import zigpy

from utils.get_logger import get_logger
from utils.misc import clamp, mutable_globals

sys.path.append(str(Path(__file__).parent))

logger = get_logger(__name__) 

SERIAL_PATH="/dev/serial/by-id/usb-Itead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_V2_1ef187a87c15f01198892bf7763d9da9-if00-port0"

class ZigbeeNetworkListener:
    """Listener for Zigbee network events such as device joins and initialization."""

    def device_joined(self, network_device):
        logger.info(f"Device joined: {network_device.ieee}")

    def device_initialized(self, network_device):
        logger.info(f"""Device initialized: {network_device.ieee}\n"
    Manufacturer: {network_device.manufacturer}
    Model: {network_device.model}""")

    def device_left(self, network_device):
        logger.info(f"Device left: {network_device.ieee}")



async def get_coordinator(serial_port_path = SERIAL_PATH) -> ControllerApplication:
    coordinator_configuration = {
        "device": { "path": serial_port_path },
        "database_path": "zigbee_network.db"
    }

    coordinator_application = await ControllerApplication.new(
        config=coordinator_configuration,
        auto_form=False
    )
    return coordinator_application


async def scan_devices(coordinator: ControllerApplication):
    """Connects to the Zigbee coordinator and prints cached attributes for all devices.

    Args:
        serial_port_path: The file path to the Zigbee adapter serial device.
    """

    for ieee_address, network_device in coordinator.devices.items():
        logger.info(f"Device: {ieee_address}")
        
        for endpoint_id, endpoint in network_device.endpoints.items():
            if endpoint_id == 0:
                continue

            assert isinstance(endpoint.in_clusters, dict)
            for cluster_id, cluster in endpoint.in_clusters.items():
                logger.info(f"  Cluster: {cluster.ep_attribute}")
                
                for attribute_id, attribute_record in cluster.attributes.items():
                    attribute_value = cluster.get(attribute_record.name)
                    
                    if attribute_value is not None:
                        logger.info(f"    {attribute_record.name}: {attribute_value}")


async def open_pairing(coordinator: ControllerApplication, permit_duration_seconds: int = 120):
    """Opens the Zigbee network for pairing and listens for joining devices.

    Args:
        serial_port_path: The file path to the Zigbee adapter serial device.
        permit_duration_seconds: How long the coordinator should allow joins.
    """
    coordinator = await get_coordinator()

    network_listener = ZigbeeNetworkListener()
    coordinator.add_listener(network_listener)

    await coordinator.permit(permit_duration_seconds)
    logger.info(f"Network open for pairing for {permit_duration_seconds} seconds. Put device in pairing mode.")

    await asyncio.sleep(permit_duration_seconds)
    logger.info("Pairing window closed.")

# if __name__ == "__main__":
#     asyncio.run(scan_devices())