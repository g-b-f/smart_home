import asyncio
from zigpy.application import ControllerApplication

async def scan_devices_and_print_attributes(serial_port_path: str):
    """Connects to the Zigbee coordinator and prints cached attributes for all devices.

    Args:
        serial_port_path: The file path to the Zigbee adapter serial device.
    """
    coordinator_configuration = {
        "device": { "path": serial_port_path },
        "database_path": "zigbee_network.db"
    }

    coordinator_application = await ControllerApplication.new(
        config=coordinator_configuration,
        auto_form=False
    )

    for ieee_address, network_device in coordinator_application.devices.items():
        print(f"Device: {ieee_address}")
        
        for endpoint_id, endpoint in network_device.endpoints.items():
            if endpoint_id == 0:
                continue
                
            for cluster_id, cluster in endpoint.in_clusters.items():
                print(f"  Cluster: {cluster.ep_attribute}")
                
                for attribute_id, attribute_record in cluster.attributes.items():
                    attribute_value = cluster.get(attribute_record.name)
                    
                    if attribute_value is not None:
                        print(f"    {attribute_record.name}: {attribute_value}")

if __name__ == "__main__":
    asyncio.run(scan_devices_and_print_attributes("/dev/ttyUSB0"))