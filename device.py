import udp_protocol as udp
import rudp_protocol as rudp
import network_layer as ntwk
import application_layer_helpers as app
import config
import queue
import struct

class Device():
    '''
    Represents a device that can send and receive messages using UDP.
    Includes and implements the necessary application layer functionalities.
    '''
    def __init__(self, port_number, ip_address, name = "Unnamed_Device", pane = "left", protocol = "UDP", worker = None):
        self.port_number = port_number
        self.ip_address = ip_address
        self.name = name
        self.pane = pane
        self.protocol = protocol
        self.worker = worker
        self.buffer = queue.Queue() # buffer to hold incoming segments until the full message can be reassembled
        ntwk.register_device(self) # register this device on the network

    def send_message(self, dest_ip, dest_port, file_path):
        '''
        Sends a message to the specified destination port with the given payload.
        The message may be corrupted with the specified chance.
        1. Read image as bytes, result is payload
        2. Split payload into chunks
        3. Encapsulate each chunk into individual UDP messages
        4. Send each UDP message to network layer
        '''
        self.worker.log_signal.emit("~ DVC: Segmenting payload...", self.pane, "info")

        # Read image as bytes to create payload
        payload_bytes = app.read_image_as_bytes(file_path)
        if payload_bytes is None:
            print("APP: payload not loaded.")
            exit()
        
        # UDP
        if self.protocol == "UDP":
            # Split payload into chunks, encapsulate each chunk into UDP segment, and send each segment to network layer
            chunks = app.split_payload(payload_bytes)

            for chunk in chunks:
                udp_datagram = udp.build_udp_segment(self.port_number, dest_port, chunk)
                
                ntwk.send(udp_datagram, dest_ip, dest_port)

                self.worker.log_signal.emit(f"~ DVC: Sending message to {dest_port} using {self.protocol}...", self.pane, "info")

            ntwk.send(b"END", dest_ip, dest_port) # send special "END" segment to indicate end of message to receiver

        # RUDP
        elif self.protocol == "RUDP":
            # Split payload into chunks
            chunks = app.split_payload(payload_bytes, 1400) # 1400 is close to standard practical limit of UDP datagram

            for i, chunk in enumerate(chunks):
                rudp_datagram = rudp.build_rudp_header(chunk, seq_num=i)
                udp_datagram = udp.build_udp_segment(self.port_number, dest_port, rudp_datagram)

                # Infinite retries for simulation - receiver will eventually ACK
                # (In real networks, we'd have finite retries to avoid infinite loops)
                retry_count = 0
                while True:
                    ntwk.send(udp_datagram, dest_ip, dest_port)
                    self.worker.log_signal.emit(f"~ DVC: Sent RUDP segment {i} (seq_num) [{i+1}/{len(chunks)}], waiting for ACK...", self.pane, "info")
                    
                    # Timeout must exceed the network delay so ACKs can arrive before retransmitting
                    ack_timeout = max(0.5, config.delay * 3 + 0.2)
                    ack_packet = rudp.wait_for_ack(i, self, dest_ip, dest_port, timeout=ack_timeout)
                    if ack_packet is not None:
                        self.worker.log_signal.emit(f"~ DVC: ACK {i} received", self.pane, "success")
                        break
                    
                    retry_count += 1
                    self.worker.log_signal.emit(f"~ DVC: Timeout waiting for ACK {i}, retransmitting... (attempt {retry_count})", self.pane, "warning")

            ntwk.send(b"END", dest_ip, dest_port)

    def receive_message(self, output_file_name, sender_ip=None):
        '''
        Receives a message and attempts to reassemble it. If successful, writes the payload to the specified output file.
        For RUDP, sender_ip and sender_port are needed to send ACK packets back.
        1. Extract header
        2. Verify port
        3. Extract payload
        4. Verify checksum  
        5. For RUDP, send ACK back to sender
        6. Put payload in buffer
        '''

        self.worker.log_signal.emit(f"~ DVC: Waiting for message...", self.pane, "info")

        payload_buffer = bytearray() # holds payloads for assembly
        expected_seq_num = 0  # tracks next expected RUDP sequence number for duplicate detection

        # Continuously listen for incoming segments until we receive the special "END" segment indicating the end of the message
        while True:
            udp_datagram = self.buffer.get()
            if udp_datagram == b"END": # if we receive the special "END" segment,
                self.worker.log_signal.emit("~ DVC: End of file received", self.pane, "info")
                break

            if self.protocol == "UDP":
                # Check destination port
                header = udp.unpack_header(udp_datagram)
                src_port = header[0]
                dest_port = header[1]

                # Verify destination port
                if dest_port != self.port_number:
                    self.worker.log_signal.emit("~ DVC: ERROR: Port unreachable", self.pane, "error")
                    continue  # don't kill receiver, just drop the segment

                self.worker.log_signal.emit(f"~ DVC: Message received from port {src_port}...", self.pane, "success")

                # Verify checksum
                is_valid = udp.validate_udp_checksum(udp_datagram)
                if not is_valid:
                    self.worker.log_signal.emit(f"~ DVC: ERROR: datagram corrupted, but continuing... (this is UDP)", self.pane, "error")
                    continue # don't kill receiver, just drop the segment
                
                # Append segment payload to buffer
                payload = udp.extract_payload(udp_datagram)
                payload_buffer.extend(payload)

            elif self.protocol == "RUDP":
                # Unpack RUDP segment
                seq_num, payload = rudp.unpack_rudp_segment(udp_datagram)
                udp_header = udp.unpack_header(udp_datagram)

                src_port = udp_header[0]
                dest_port = udp_header[1]

                # Verify destination port
                if dest_port != self.port_number:
                    self.worker.log_signal.emit("~ DVC: ERROR: Port unreachable", self.pane, "error")
                    continue  # don't kill receiver, just drop the segment

                self.worker.log_signal.emit(f"~ DVC: RUDP segment {seq_num} received from port {src_port}...", self.pane, "success")

                is_valid = udp.validate_udp_checksum(udp_datagram) # validate checksum of the entire UDP datagram
                if not is_valid:
                    self.worker.log_signal.emit(f"~ DVC: ERROR: datagram corrupted, dropping and waiting for retransmission... (RUDP)", self.pane, "error")
                    continue # don't kill receiver, just drop the segment

                # Send ACK back to sender (always ACK valid segments, even duplicates)
                if sender_ip and src_port:
                    ack_packet = rudp.build_ack_packet(seq_num)
                    ack_udp_segment = udp.build_udp_segment(self.port_number, src_port, ack_packet)
                    ntwk.send(ack_udp_segment, sender_ip, src_port)
                    self.worker.log_signal.emit(f"~ DVC: ACK {seq_num} sent to sender", self.pane, "info")

                # Only append new segments; discard duplicates from retransmissions
                if seq_num == expected_seq_num:
                    payload_buffer.extend(payload)
                    expected_seq_num += 1
                else:
                    self.worker.log_signal.emit(f"~ DVC: Duplicate segment {seq_num} (expected {expected_seq_num}), discarding data", self.pane, "warning")

        # Reassemble payload and return output file
        with open(output_file_name, "wb") as f:
            f.write(payload_buffer)

        self.worker.log_signal.emit("~ DVC: File assembled", self.pane, "info")

        self.buffer.queue.clear() # clear buffer for next message

        return output_file_name

    def get_port_number(self):
        return self.port_number
    
    def set_port_number(self, port_number):
        self.port_number = port_number

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name