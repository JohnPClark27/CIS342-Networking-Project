import transport_layer_udp as udp
import network_layer as ntwk
import time
import ipaddress
from gui import MainWindow
import application_layer_helpers as app

class Device():
    '''
    Represents a device that can send and receive messages using UDP.
    Includes and implements the necessary application layer functionalities.
    '''
    def __init__(self, port_number, ip_address = ipaddress.IPv4Address("127.0.0.1"), name = "Unnamed_Device", window = None, pane = "left"):
        self.port_number = port_number
        self.ip_address = ip_address
        self.name = name
        self.window = window
        self.pane = pane
        self.buffer = [] # buffer to hold received segments until the message is finalized
        ntwk.register_device(self) # register this device on the network

    def send_message(self, dest_ip, dest_port, payload, corrupt_chance = 0):
        '''
        Sends a message to the specified destination port with the given payload.
        The message may be corrupted with the specified chance.
        1. Read image as bytes, result is payload
        2. Split payload into chunks
        3. Encapsulate each chunk into individual UDP messages
        4. Send each UDP message to network layer
        '''
        self.window.write_log(f"~ DVC: Preparing message...", self.pane, "info")

        payload_bytes = app.read_image_as_bytes(payload)
        if payload_bytes is None:
            print("APP: payload not loaded.")
            exit()
        
        self.window.write_log(f"~ DVC: Sending message to {dest_port}...", self.pane, "info")

        chunks = app.split_payload(payload_bytes)
        for chunk in chunks:
            segment = udp.calc_segment(self.port_number, dest_port, chunk)
            
            ntwk.send(segment, dest_ip, dest_port, corrupt_chance)



    def receive_message(self, segment):
        '''
        Receives a message and attempts to reassemble it. If successful, writes the payload to the specified output file.
        1. Extract header
        2. Verify port
        3. Extract payload
        4. Verify checksum
        5. Put payload in buffer
        '''

        self.window.write_log(f"~ DVC: Waiting for message...", self.pane, "info")

        ntwk.recv(segment) # remove?

        # Check destination port
        header = udp.unpack_header(segment)
        src_port = header[0]
        dest_port = header[1]

        if dest_port == self.port_number:
            self.window.write_log(f"~ DVC: Message received from port {src_port}...", self.pane, "success")
        else:
            self.window.write_log(f"~ DVC: ERROR: Port unreachable", self.pane, "error")
            return

        # Verify checksum
        is_valid = udp.verify_checksum(segment)
        if is_valid is None:
            self.window.write_log(f"~ DVC: ERROR: datagram corrupted, but continuing... (this is UDP)", self.pane, "error")
            return
        
        # Append segment to buffer
        data = udp.extract_payload(segment)
        self.buffer.append(data)



    def finalize_message(self, output_file_name):
        '''
        After all segments have been received, reassembles the payload and writes it to the specified output file.
        '''
        image_bytes = b"".join(self.buffer)

        with open(output_file_name, "wb") as f:
            f.write(image_bytes)

        self.window.write_log(f"~ DVC: Message received...", self.pane, "success")

        self.buffer.clear()



    def get_port_number(self):
        return self.port_number
    
    def set_port_number(self, port_number):
        self.port_number = port_number

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name