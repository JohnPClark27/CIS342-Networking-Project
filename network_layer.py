"""
This module is a pseudo-network layer. It provides functionality to send messages over the network, with a chance of corruption during transmission.
"""
import random, time

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

def send(message, dest_ip, dest_port, corrupt_chance = 0, delay = 0):
    '''
    Simulates sending a message over a network. The message may be corrupted with the specified chance.
    '''
    print(f"NTWK: Transmitting message...")

    time.sleep(delay) # simulate some delay

    if random.randint(0, 100) < corrupt_chance:
        print("NTWK: Message corrupted during transmission.")
        message = corrupt_segment(message) # corrupt something

    key = (str(dest_ip), dest_port)

    if key in devices:
        devices[key].receive_message(message)
    else:
        print("NTWK: Destination unreachable (likely unknown IP).")
    
def recv(message):
    '''
    Simulates receiving a message from a network. Currently purely an in-between step for simulation purposes.
    '''
    return message