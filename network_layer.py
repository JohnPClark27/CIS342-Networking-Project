
from email import message
import random
import struct

def corrupt_segment(segment):
    '''
    Returns a corrupted version of the segment by flipping a random bit in the payload.
    '''
    corrupted = bytearray(segment)

    index = random.randint(8, len(segment) - 1) # avoid header
    corrupted[index] ^= 0xFF

    return bytes(corrupted)

def send(message, corrupt_chance = 0):
    '''
    Simulates sending a message over the network. Randomly corrupts the message with a specified chance.
    '''
    if random.random() < corrupt_chance:
        print("Message corrupted during transmission.")
        message[0] = corrupt_segment(message[0]) # corrupt a segment corrupt_segment(message, corrupt_chance)
        return message
    else:
        print("Message sent successfully.")
        return message