"""
This module is a pseudo-network layer. It provides functionality to send messages over the network, with a chance of corruption during transmission.
"""
import random

def corrupt_segment(segment):
    '''
    Returns a corrupted version of the segment by flipping a random bit in the payload.
    '''
    corrupted = bytearray(segment)

    index = random.randint(8, len(segment) - 1) # avoid header
    corrupted[index] ^= 0xFF # flip all bits in the byte at the random index to corrupt the segment

    return bytes(corrupted)

def send(message, corrupt_chance = 0):
    '''
    Simulates sending a message over the network. Randomly corrupts the first chunk of the message with a specified chance.
    '''
    if random.random() < corrupt_chance:
        print("NTWK: Message corrupted during transmission.")
        message[0] = corrupt_segment(message[0]) # corrupt a segment
        return message
    else:
        print("NTWK: Message sent successfully.")
        return message
    
def recv(message):
    '''
    Simulates receiving a message from a network. Currently purely an in-between step for simulation purposes.
    '''
    return message