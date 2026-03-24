import random
import struct

HEADER_FORMAT = '!HHHH'
PAYLOAD_CHUNK_SIZE = 65527

# def read_image_as_bytes(file_path):
#     '''
#     Given an image file path, returns a string of bytes representing the image.
#     '''
#     try:
#         with open(file_path, 'rb') as f:
#             image_bytes = f.read()
#         return image_bytes
#     except FileNotFoundError:
#         print(f"Error: File not found at {file_path}")
#         return None
    
# def write_bytes_to_image(payload_bytes, output_path):
#     '''
#     Given a string of bytes representing an image, returns the image at the specified path
#     '''
#     with open(output_path, "wb") as f:
#         f.write(payload_bytes)

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

def pack_header(src_port, dest_port, payload_length, checksum = 0):
    '''
    Packs a UDP-style header containing source port, destination port,
    segment length (header + payload), and checksum into 8 bytes.
    '''
    length = 8 + payload_length
    result = struct.pack(HEADER_FORMAT, src_port, dest_port, length, checksum)
    return result

def split_payload(payload):
    '''
    Splits the payload into chunks of size PAYLOAD_CHUNK_SIZE (65527 bytes).
    '''
    chunks = []
    for i in range(0, len(payload), PAYLOAD_CHUNK_SIZE):
        chunks.append(payload[i:i+PAYLOAD_CHUNK_SIZE])
    return chunks

def calc_segment(src_port, dest_port, payload_bytes):
    '''
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

    total = 0
    for i in range(0, len(segment), 2):
        word = int.from_bytes(segment[i:i+2], byteorder="big", signed=False)
        total += word
        if (total > 0xFFFF):
            total = (total & 0xFFFF) + (total >> 16)

    if total == 0xFFFF:
        return True
    else:
        return False

def corrupt_segment(segment):
    '''
    Returns a corrupted version of the segment by flipping a random bit in the payload.
    '''
    corrupted = bytearray(segment)

    index = random.randint(8, len(segment) - 1) # avoid header
    corrupted[index] ^= 0xFF

    return bytes(corrupted)

# === SENDER/RECEIVER FUNCTIONS ===
def create_message(src_port, dest_port, payload):
    payload_bytes = payload.encode("utf-8")
    if payload_bytes is None:
        print("payload not loaded")
        exit()

    segments = []
    chunks = split_payload(payload_bytes)
    for chunk in chunks:
        segments.append(calc_segment(src_port, dest_port, chunk))

    # segments[0] = corrupt_segment(segments[0]) # corrupt a segment

    return segments

def reassemble_message(segments, output_file_name = "reassembled.png"):
    reassembled = bytearray()

    for segment in segments:
        if verify_checksum(segment):
            reassembled.extend(extract_payload(segment))
        else:
            print("Invalid segment detected")
        
    print(f"Received message:", reassembled.decode())