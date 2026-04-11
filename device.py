import udp_protocol as udp
import network_layer as ntwk
import ipaddress
import application_layer_helpers as app
import queue

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
                segment = udp.build_udp_segment(self.port_number, dest_port, chunk)
                
                ntwk.send(segment, dest_ip, dest_port)

                self.worker.log_signal.emit(f"~ DVC: Sending message to {dest_port} using {self.protocol}...", self.pane, "info")


            ntwk.send(b"END", dest_ip, dest_port) # send special "END" segment to indicate end of message to receiver

        # RUDP
        if self.protocol == "RUDP":
            # Split payload into chunks, encapsulate each chunk into RUDP segment, and send each segment to network layer
            pass # RUDP not implemented yet, but can be added similarly to UDP with additional logic for acknowledgments and retransmissions as needed

    def receive_message(self, output_file_name):
        '''
        Receives a message and attempts to reassemble it. If successful, writes the payload to the specified output file.
        1. Extract header
        2. Verify port
        3. Extract payload
        4. Verify checksum
        5. Put payload in buffer
        '''

        self.worker.log_signal.emit(f"~ DVC: Waiting for message...", self.pane, "info")

        payload_buffer = bytearray() # holds payloads for assembly

        # Continuously listen for incoming segments until we receive the special "END" segment indicating the end of the message
        while True:
            segment = self.buffer.get()
            if segment == b"END": # if we receive the special "END" segment,
                self.worker.log_signal.emit("~ DVC: End of file received", self.pane, "info")
                break

            else:
                # Check destination port
                header = udp.unpack_header(segment)
                src_port = header[0]
                dest_port = header[1]

                # Verify destination port
                if dest_port != self.port_number:
                    self.worker.log_signal.emit("~ DVC: ERROR: Port unreachable", self.pane, "error")
                    continue  # don't kill receiver, just drop the segment

                self.worker.log_signal.emit(f"~ DVC: Message received from port {src_port}...", self.pane, "success")

                # Verify checksum
                is_valid = udp.validate_udp_checksum(segment)
                if not is_valid:
                    self.worker.log_signal.emit(f"~ DVC: ERROR: datagram corrupted, but continuing... (this is UDP)", self.pane, "error")
                    continue # don't kill receiver, just drop the segment
                
                # Append segment payload to buffer
                payload = udp.extract_payload(segment)
                payload_buffer.extend(payload)

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