"""
This module is a pseudo-network layer. It provides functionality to send messages over the network, with a chance of corruption during transmission.
"""
import random, time

def corrupt_segment(segment):
    '''
    Returns a corrupted version of the segment by flipping a random bit in the payload.
    '''
    corrupted = bytearray(segment)

    if len(segment) > 8:
        index = random.randint(8, len(segment) - 1) # avoid header
        corrupted[index] ^= 0xFF # flip all bits in the byte at the random index to corrupt the segment
    else:
        corrupted[0] ^= 0xFF

    return bytes(corrupted)

def send(segment, channel, corrupt_chance = 0, drop_chance = 0, delay = 0.001):
    '''
    Simulates sending a message over the network. Randomly corrupts the first chunk of the message with a specified chance.
    '''
    print(f"NTWK: Received send() request...")

    time.sleep(delay) # simulate some delay

    roll = random.randint(1, 100)
    if roll < corrupt_chance:
        print("NTWK: Message corrupted during transmission.")
        segment = corrupt_segment(segment) # corrupt a segment
        channel.put(segment)
    elif roll < drop_chance+corrupt_chance:
        print("NTWK: Message dropped during transmission.")
    else:
        print("NTWK: Message transmitted successfully.")
        channel.put(segment)