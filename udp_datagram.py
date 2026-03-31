"""
This module implements a simulation of UDP.
"""
import struct

HEADER_FORMAT = '!HHHH'
PAYLOAD_CHUNK_SIZE = 65527

# === Helper functions for image payloads ===
def read_image_as_bytes(file_path):
    '''
    Given an image file path, returns a string of bytes representing the image.
    '''
    try:
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        return image_bytes
    except FileNotFoundError:
        print(f"UDP: Error: File not found at {file_path}")
        return None
    
# def write_bytes_to_image(payload_bytes, output_path):
#     '''
#     Given a string of bytes representing an image, returns the image at the specified path
#     '''
#     with open(output_path, "wb") as f:
#         f.write(payload_bytes)

# === Extracts parts from segments ===
def extract_payload(segment):
    '''
    Returns payload bytes from segment
    '''
    return segment[8:]

def extract_header(segment):
    '''
    Returns header bytes from segment
    '''
    return segment[:8]

def split_payload(payload):
    '''
    Splits the payload into chunks of size PAYLOAD_CHUNK_SIZE (65527 bytes).
    '''
    chunks = []
    for i in range(0, len(payload), PAYLOAD_CHUNK_SIZE):
        chunks.append(payload[i:i+PAYLOAD_CHUNK_SIZE])
    return chunks

# === Main UDP functions ===

def pack_header(src_port, dest_port, payload_length, checksum = 0):
    '''
    Packs a UDP-style header containing source port, destination port,
    segment length (header + payload), and checksum into 8 bytes.
    '''
    length = 8 + payload_length
    result = struct.pack(HEADER_FORMAT, src_port, dest_port, length, checksum)
    return result

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
        return True
    else:
        return False

def create_message(src_port, dest_port, payload):
    '''
    Creates a UDP message with the specified source port, destination port, and payload.
    The payload is read from an image file and split into chunks if necessary.
    Each chunk is packed into a segment with a header containing the source port, destination port, length, and checksum.
    Returns a list of segments representing the complete message.
    '''
    payload_bytes = read_image_as_bytes(payload)
    if payload_bytes is None:
        print("UDP: payload not loaded.")
        exit()

    segments = []
    chunks = split_payload(payload_bytes)
    for chunk in chunks:
        segments.append(calc_segment(src_port, dest_port, chunk))

    return segments

def reassemble_message(segments):
    '''
    Given a list of segments, verifies the checksum of each segment and reassembles the payload if the segment is valid.
    Returns None if corrupted, and a struct containing the header fields and the payload (in bytes) if not
    '''
    reassembled = bytearray() # using bytearray for efficient concatenation of bytes

    was_corrupted = False

    # Extracting header
    header = extract_header(segments[0])
    # print("UDP: Header (binary): ", header)
    unpacked_header = struct.unpack(HEADER_FORMAT, header)
    print("UDP: Header (unpacked): ", unpacked_header)
    # print("src_port: ", unpacked_header[0])
    # print("dest_port: ", unpacked_header[1])
    # print("payload_length: ", unpacked_header[2])
    # print("checksum: ", unpacked_header[3])

    for segment in segments:
        if verify_checksum(segment):
            reassembled.extend(extract_payload(segment))
        else:
            was_corrupted = True
            break

    if was_corrupted:
        print("UDP: Invalid segment detected.")
        return None
    else:
        print("UDP: Message successfully reassembled...")
        return unpacked_header, reassembled