import asyncio
import bellows.zigbee.application
import zhaquirks
import logging
# Register custom device handlers for non-standard dials and remotes

logging.basicConfig(
    format="%(asctime)s %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    force=True,
    level="INFO"
)

logger = logging.getLogger(__name__)

def setup():
    logger.info("setting up zhaquirks")
    zhaquirks.setup()
    logger.info("finished setup")


class DialEventListener:
    """Captures and logs incoming commands and attribute updates from a dial cluster."""

    def __init__(self, device_ieee: str, cluster_name: str):
        self.device_ieee = device_ieee
        self.cluster_name = cluster_name

    def attribute_updated(self, attribute_id: int, attribute_value: any):
        print(f"[{self.device_ieee}] {self.cluster_name} Attribute {attribute_id} changed to: {attribute_value}")

    def zcl_command(self, header, args):
        command_name = getattr(header, "command_id", header)
        print(f"[{self.device_ieee}] {self.cluster_name} Command Received -> ID: {command_name}, Args: {args}")


async def bind_dial_out_clusters(network_device):
    """Binds all client (out) clusters of a device to the coordinator.

    Args:
        network_device: The zigpy device instance representing the smart dial.
    """
    logger.info(f"Beginning cluster binding for device: {network_device.ieee}")
    logger.info("Press or turn the dial repeatedly now to keep the device awake...")

    for endpoint_id, endpoint in network_device.endpoints.items():
        if endpoint_id == 0:
            continue

        for cluster_id, cluster in endpoint.out_clusters.items():
            try:
                await cluster.bind()
                logger.info(f"Successfully bound cluster {cluster.ep_attribute} (ID: {cluster_id})")
            except Exception as exception:
                logger.error(f"Failed to bind cluster {cluster.ep_attribute}: {exception}")


async def setup_dial_listeners_and_bind(serial_port_path: str, target_device_ieee: str):
    """Initializes coordinator, attaches event listeners, and executes binding on target device.

    Args:
        serial_port_path: Path to serial device.
        target_device_ieee: IEEE address string of the smart dial to bind.
    """
    coordinator_configuration = {
        "device": {
            "path": serial_port_path
        },
        "database_path": "zigbee_network.db"
    }

    coordinator_application = await bellows.zigbee.application.ControllerApplication.new(
        config=coordinator_configuration,
        auto_form=False
    )

    for ieee_address, network_device in coordinator_application.devices.items():
        is_target_device = str(ieee_address) == target_device_ieee

        for endpoint_id, endpoint in network_device.endpoints.items():
            if endpoint_id == 0:
                continue

            # Attach listeners to both in_clusters and out_clusters
            for cluster_id, cluster in endpoint.out_clusters.items():
                event_listener = DialEventListener(str(ieee_address), cluster.ep_attribute)
                cluster.add_listener(event_listener)

            for cluster_id, cluster in endpoint.in_clusters.items():
                event_listener = DialEventListener(str(ieee_address), cluster.ep_attribute)
                cluster.add_listener(event_listener)

        if is_target_device:
            await bind_dial_out_clusters(network_device)

    logger.info("Listening for incoming dial commands...")
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    # Replace with the actual IEEE address of your dial printed during pairing
    logger.info("starting")
    setup()
    TARGET_DIAL_IEEE = "94:a0:81:ff:fe:d2:ea:46"
    asyncio.run(setup_dial_listeners_and_bind("/dev/ttyUSB0", TARGET_DIAL_IEEE))

