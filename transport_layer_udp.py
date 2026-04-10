"""
This module implements a simulation of UDP.
This UDP simulation includes:
+ Encapsulating data into datagrams
+ Calculating and validating checksums
"""
import struct

HEADER_FORMAT = '!HHHH'
PAYLOAD_CHUNK_SIZE = 65527

# === Extracts parts from segments ===
def extract_payload(segment): #extract_udp_payload
    '''
    Returns payload bytes from segment
    '''
    return segment[8:]

def extract_header(segment): #extract_udp_header
    '''
    Returns header bytes from segment
    '''
    return segment[:8]

# === Header functions ===
def pack_header(src_port, dest_port, payload_length, checksum = 0):
    '''
    Packs a UDP-style header containing source port, destination port,
    segment length (header + payload), and checksum into 8 bytes.
    '''
    length = 8 + payload_length
    packed_header = struct.pack(HEADER_FORMAT, src_port, dest_port, length, checksum)
    
    # print("UDP: Header (packed, binary): ", packed_header)

    return packed_header

def unpack_header(segment):
    '''
    Unpacks a UDP-style header from 8 bytes into a tuple of (src_port, dest_port, length, checksum).
    '''
    header = extract_header(segment)
    unpacked_header = struct.unpack(HEADER_FORMAT, header)

    # print("UDP: Header (unpacked): ", unpacked_header)

    return unpacked_header

# === Payload, Checksum, and Encapsulation functions ===
def calc_segment(src_port, dest_port, payload_bytes):
    '''
    Given source port, destination port, and payload bytes, calculates the checksum and returns a complete UDP segment as bytes.
    The UDP

    segment format:
    [0–1]   src_port
    [2–3]   dest_port
    [4–5]   length
    [6–7]   checksum
    [8–...] payload/data divided into chunks of 65527 (65535 - 8 byte UDP header)
    '''

    payload_length = len(payload_bytes)
    header_bytes = pack_header(src_port, dest_port, payload_length)
    segment = header_bytes + payload_bytes

    if len(segment) % 2 == 1:
        segment = segment + b'\x00' # add a padding 0 bit if length of segment is odd

    total = 0
    for i in range(0, len(segment), 2):
        word = int.from_bytes(segment[i:i+2], byteorder="big", signed=False)
        total += word
        # print(hex(word))
        if (total > 0xFFFF):
            total = (total & 0xFFFF) + (total >> 16)

    # Compute final checksum: take one's complement and keep the result 16-bit
    checksum = ~total
    checksum = checksum & 0xFFFF

    udp_header = pack_header(src_port, dest_port, payload_length, checksum)
    udp_segment = udp_header + payload_bytes

    return udp_segment

def verify_checksum(segment):
    '''
    Verifies the checksum of a segment. Returns True if the checksum is valid, False otherwise.
    '''
    if len(segment) % 2 == 1:
        segment = segment + b'\x00' # add a padding 0 bit if length of segment is odd

    # Calculate the checksum of the segment. If the result is 0xFFFF, the segment is valid.
    total = 0
    for i in range(0, len(segment), 2):
        word = int.from_bytes(segment[i:i+2], byteorder="big", signed=False) # network byte order is big-endian, checksum is unsigned
        total += word
        if (total > 0xFFFF): # handle overflow by adding carry back to total
            total = (total & 0xFFFF) + (total >> 16)

    if total == 0xFFFF:
        return segment
    else:
        return None