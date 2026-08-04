import asyncio
import logging
from bellows.zigbee.application import ControllerApplication

# Enable logging to see underlying Zigbee stack communications
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class ZigbeeJoinListener:
    """Listens for network event callbacks triggered by zigpy."""
    
    def __init__(self, application):
        self.application = application

    def device_joined(self, device):
        """Triggered immediately when a device physically connects to the radio network."""
        print(f"\n[ALERT] Device joined the network! IEEE: {device.ieee}, NWK: {device.nwk}\n")

    def device_initialized(self, device, new=True):
        """Triggered after zigpy completes interviewing the device's endpoints and clusters."""
        if new:
            print(f"\n[SUCCESS] New device fully initialized! Model: {device.model}, Manufacturer: {device.manufacturer}\n")


async def main():
    # Define configuration matching your adapter and database file position
    config = ControllerApplication.SCHEMA({
        "database_path": "zigbee_devices.db",
        "device": {
            "path": "/dev/ttyUSB0",  # Change this to your exact Silicon Labs adapter path
            "baudrate": 115200       # Standard baudrate for EZSP radios
        }
    })

    print("Initializing ControllerApplication via bellows...")
    app = await ControllerApplication.new(config=config, auto_form=True, start_radio=True)
    
    # Register our listener to capture the join prints
    listener = ZigbeeJoinListener(app)
    app.add_listener(listener)

    # Open the network for pairing
    pairing_duration = 60
    print(f"Opening pairing window for {pairing_duration} seconds...")
    print("Put your Zigbee device into pairing mode now.")
    await app.permit(pairing_duration)

    # Wait for the pairing window to complete
    await asyncio.sleep(pairing_duration)
    print("Pairing window closed.")
    
    # Properly shut down the radio connection before exiting
    await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting.")

