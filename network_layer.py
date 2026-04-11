"""
This module is a pseudo-network layer. It provides functionality to send datagrams over the network, with a chance of corruption during transmission.
"""
import random, time
import config

devices = {} # maps (ip, port) to device

def register_device(device):
    '''
    Registers a device on the network by adding it to the devices dictionary.
    '''
    devices[(str(device.ip_address), device.port_number)] = device

def corrupt_segment(segment):
    '''
    Returns a corrupted version of the segment by flipping a random bit in the payload.
    '''
    corrupted = bytearray(segment)

    index = random.randint(8, len(segment) - 1) # avoid header
    corrupted[index] ^= 0xFF # flip all bits in the byte at the random index to corrupt the segment

    return bytes(corrupted)

def send(datagram, dest_ip, dest_port):
    '''
    Simulates sending a datagram over a network. The datagram may be corrupted with the specified chance.
    '''
    # Get current corruption and drop chances and delay from config
    # This is more realistic, and allows the chances and delay to be dynamically adjusted from the GUI and ensures that the most up-to-date values are used for each transmission.
    corrupt_chance = config.corruption_chance
    drop_chance = config.drop_chance
    delay = config.delay

    print(f"NTWK: Sending datagram...")

    # Lookup destination device based on dest_ip and dest_port
    dest_device = devices.get((str(dest_ip), dest_port))
    if dest_device is None:
        print(f"NTWK: ERROR: Destination device with IP {dest_ip} and port {dest_port} not found on the network.")
        return
    
    time.sleep(delay) # simulate some delay

    # Handle END marker specially - always deliver it without corruption or dropping
    if datagram == b"END":
        print("NTWK: END marker sent successfully.")
        dest_device.buffer.put(datagram)
        return

    roll = random.randint(0, 100)
    if roll < corrupt_chance:
        print("NTWK: datagram corrupted during transmission!")
        datagram = corrupt_segment(datagram) # corrupt the segment
        dest_device.buffer.put(datagram) # deliver the corrupted segment to the destination device's buffer
    elif roll < corrupt_chance + drop_chance:
        print("NTWK: datagram dropped during transmission!")
        return # drop the segment by not delivering it to the destination device
    else:
        print("NTWK: datagram sent successfully.")
        dest_device.buffer.put(datagram) # deliver the segment to the destination device's buffer