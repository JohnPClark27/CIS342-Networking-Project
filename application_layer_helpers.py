"""
Helper functions for the application layer of the simulation.
This is not a 1:1 implementation of any specific application layer protocol, but rather a collection of functions that provide the necessary functionality for the simulation.
"""

PAYLOAD_CHUNK_SIZE = 65527

def read_image_as_bytes(file_path):
    '''
    Given an image file path, returns a string of bytes representing the image.
    '''
    try:
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        return image_bytes
    except FileNotFoundError:
        print(f"APP: Error: File not found at {file_path}")
        return None
    
def split_payload(payload):
    '''
    Splits the payload into chunks of size PAYLOAD_CHUNK_SIZE.
    '''
    chunks = []
    for i in range(0, len(payload), PAYLOAD_CHUNK_SIZE):
        chunks.append(payload[i:i+PAYLOAD_CHUNK_SIZE])
    return chunks