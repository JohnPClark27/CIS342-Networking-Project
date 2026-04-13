"""
RUDP Protocol Implementation
Implements reliable UDP with sequence numbers, ACKs, and retransmission on timeout.
"""

import struct, time
import udp_protocol as udp

# ACK format: b"ACK" prefix + 4-byte sequence number
ACK_PREFIX = b"ACK"

def build_rudp_header(chunk, seq_num):
    '''Builds RUDP header with sequence number and payload.'''
    rudp_header = struct.pack('!I', seq_num) # 4 byte sequence number in big-endian
    rudp_segment = rudp_header + chunk
    return rudp_segment

def build_ack_packet(seq_num):
    '''Builds an ACK packet for the given sequence number.'''
    ack_payload = ACK_PREFIX + struct.pack('!I', seq_num)
    return ack_payload

def is_ack_packet(packet):
    '''Checks if a packet is an ACK packet.'''
    return isinstance(packet, bytes) and len(packet) >= len(ACK_PREFIX) and packet[:len(ACK_PREFIX)] == ACK_PREFIX

def extract_ack_seq_num(ack_packet):
    '''
    Extracts sequence number from ACK packet.
    Returns the sequence number as an integer, or None if packet is not a valid ACK.
    '''
    if is_ack_packet(ack_packet) and len(ack_packet) >= len(ACK_PREFIX) + 4:
        return struct.unpack('!I', ack_packet[len(ACK_PREFIX):len(ACK_PREFIX)+4])[0]
    return None

def unpack_rudp_segment(udp_datagram):
    '''
    Unpacks a RUDP segment from UDP datagram.
    Returns (seq_num, payload_bytes) where seq_num is the 4-byte sequence number
    and payload_bytes is the actual data (without RUDP header).
    '''
    udp_payload = udp.extract_payload(udp_datagram)
    
    if len(udp_payload) < 4:
        raise ValueError("Invalid RUDP segment: payload too short")
    
    # First 4 bytes are RUDP sequence number
    rudp_seq_num = struct.unpack('!I', udp_payload[:4])[0]
    
    # Remaining bytes are payload
    payload_bytes = udp_payload[4:]
    
    return rudp_seq_num, payload_bytes

def wait_for_ack(expected_seq, device, sender_dest_ip, sender_dest_port, timeout=0.2):
    '''
    Waits for an ACK packet with the expected sequence number in the device's buffer.
    Returns True if matching ACK received, False if timeout occurs.
    Device's buffer will contain ACK packets wrapped in UDP datagrams sent from
    receiver back to sender, so we must extract the UDP payload before checking.
    Optimized for local simulation: uses 200ms timeout and fast polling.
    '''
    start_time = time.time()
    pending_packets = []  # Buffer to hold non-matching packets
    
    while time.time() - start_time < timeout:
        try:
            # Get packet from device buffer with very short timeout for fast polling
            packet = device.buffer.get(timeout=0.01)
            
            # ACKs arrive as full UDP datagrams — extract the payload first
            payload = udp.extract_payload(packet) if isinstance(packet, bytes) and len(packet) > 8 else packet

            if not udp.validate_udp_checksum(packet):
                return None  # Invalid packet, ignore and continue waiting

            # Check if the payload is an ACK packet
            if is_ack_packet(payload):
                ack_seq = extract_ack_seq_num(payload)
                if ack_seq == expected_seq:
                    # Found the ACK we want! Put back any pending packets first
                    for pending in pending_packets:
                        device.buffer.put(pending)
                    return True
                else:
                    # Not the ACK we're waiting for, save it
                    pending_packets.append(packet)
            else:
                # Not an ACK, save it
                pending_packets.append(packet)
        except:
            # Queue get timeout, just continue waiting
            time.sleep(0.001)  # Sleep 1ms to prevent busy-waiting
            continue
    
    # Timeout occurred, put all packets back
    for pending in pending_packets:
        device.buffer.put(pending)
    return None