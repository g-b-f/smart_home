import socket
import asyncio

async def query_bulb(ip):
    UDP_PORT = 38899
    MESSAGE = '{"method":"getPilot","params":{}}'

    print("UDP target IP: %s" % ip)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)  # Make socket non-blocking for async operations
    
    try:
        # Send the message
        await asyncio.get_event_loop().sock_sendto(sock, MESSAGE.encode(), (ip, UDP_PORT))
        
        # Receive the response
        data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 1024)
        print("received message: %s" % data)
    except Exception as e:
        print(f"Error querying bulb at {ip}: {e}")
    finally:
        sock.close()

async def main():
    ips = ["192.168.1.100", "192.168.1.101", "192.168.1.104"]
    
    # Create tasks for concurrent execution
    tasks = [query_bulb(ip) for ip in ips]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

    # cc408525d286