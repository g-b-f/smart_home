import asyncio
from pathlib import Path
import sys
from zigpy.device import Device
from zigpy.endpoint import Endpoint
from zigpy.zcl import Cluster
from zigpy.application import ControllerApplication as ZigPyController
from bellows.zigbee.application import ControllerApplication

from utils.get_logger import get_logger
from utils.misc import clamp, mutable_globals

sys.path.append(str(Path(__file__).parent))

logger = get_logger(__name__, "DEBUG") 

SERIAL_PATH="/dev/serial/by-id/usb-Itead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_V2_1ef187a87c15f01198892bf7763d9da9-if00-port0"


import asyncio

class ZigbeeEventLogger:
    """Logs asynchronous attribute updates and commands from a Zigbee cluster.
    
    Args:
        ieee_address: The IEEE address of the device.
        cluster_name: The name of the cluster emitting the event.
    """
    def __init__(self, ieee_address: str, cluster_name: str):
        self.ieee_address = ieee_address
        self.cluster_name = cluster_name
        
    def attribute_updated(self, attribute_id: int, attribute_value):
        logger.info(f"Device {self.ieee_address} updated {self.cluster_name} attribute {attribute_id} to {attribute_value}")
        
    def zcl_command(self, command_id: int, command_arguments: tuple):
        logger.info(f"Device {self.ieee_address} sent {self.cluster_name} command {command_id} with {command_arguments}")


async def attach_zigbee_listeners(coordinator: ZigPyController) -> None:
    """Iterates through all known devices and attaches listeners to their clusters.
    
    Args:
        coordinator: The initialized Zigbee coordinator application.
    """
    for ieee_address, network_device in coordinator.devices.items():
        for endpoint_id, endpoint in network_device.endpoints.items():
            if endpoint_id == 0:
                continue
            message = []

            assert isinstance(endpoint, Endpoint)
            message.append(f"Attaching listeners for device {ieee_address}, endpoint {endpoint_id}")
            for cluster in endpoint.clusters:
                message.append(f"  cluster {cluster.ep_attribute}")
                event_logger = ZigbeeEventLogger(str(ieee_address), cluster.ep_attribute)
                cluster.add_listener(event_logger)
            logger.debug("\n".join(message))

class ZigbeeNetworkListener:
    """Listener for Zigbee network events such as device joins and initialization."""

    def device_joined(self, network_device: Device) -> None:
        logger.info(f"Device joined: {network_device.ieee}")

    def device_initialized(self, network_device: Device) -> None:
        logger.info(f"""Device initialized: {network_device.ieee}
    Manufacturer: {network_device.manufacturer}
    Model: {network_device.model}""")

    def device_left(self, network_device: Device) -> None:
        logger.info(f"Device left: {network_device.ieee}")



async def get_coordinator(serial_port_path = SERIAL_PATH) -> ZigPyController:
    coordinator_configuration = {
        "device": { "path": serial_port_path },
        "database_path": "zigbee_network.db"
    }

    coordinator_application = await ControllerApplication.new(
        config=coordinator_configuration,
        auto_form=False
    )
    return coordinator_application


async def scan_devices(coordinator: ZigPyController):
    """Connects to the Zigbee coordinator and prints cached attributes for all devices.

    Args:
        serial_port_path: The file path to the Zigbee adapter serial device.
    """
    message=[]
    indent_1 = " "*2
    indent_2 = " "*4

    for ieee_address, network_device in coordinator.devices.items():
        message.append(f"Device: {ieee_address}")

        for endpoint_id, endpoint in network_device.endpoints.items():
            if endpoint_id == 0:
                continue

            assert isinstance(endpoint, Endpoint)
            in_clusters: dict[int, Cluster] = endpoint.in_clusters
            for cluster in in_clusters.values():
                message.append(f"{indent_1}Cluster: {cluster.ep_attribute}")
                
                for attribute_record in cluster.attributes.values():
                    attribute_value = cluster.get(attribute_record.name)
                    
                    if attribute_value is not None:
                        message.append(f"{indent_2}{attribute_record.name}: {attribute_value}")

    logger.info("\n".join(message))


async def open_pairing(permit_duration_seconds: int = 120):
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

if __name__ == "__main__":
    asyncio.run(open_pairing())