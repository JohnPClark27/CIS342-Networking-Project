import udp_datagram as udp
import network_layer as ntwk
import time
import ipaddress
from gui import MainWindow

class Device():
    '''
    Represents a device that can send and receive messages using UDP.
    '''
    def __init__(self, port_number, ip_address = ipaddress.IPv4Address("127.0.0.1"), name = "Unnamed_Device", window = None, pane = "left"):
        self.port_number = port_number
        self.ip_address = ip_address
        self.name = name
        self.window = window
        self.pane = pane

    def send_message(self, dest_port, payload, corrupt_chance = 0):
        '''
        Sends a message to the specified destination port with the given payload.
        The message may be corrupted with the specified chance.
        '''
        self.window.write_log(f"~ DVC: Preparing message...", self.pane, "info")
        udp_datagram = udp.create_message(self.port_number, dest_port, payload)
        self.window.write_log(f"~ DVC: Sending message to {dest_port}...", self.pane, "info")
        return (ntwk.send(udp_datagram, corrupt_chance))

    def receive_message(self, message, output_file_name):
        '''
        Receives a message and reassembles it into the original payload.
        The reassembled payload is saved to the specified output file name.
        '''

        self.window.write_log(f"~ DVC: Waiting for message...", self.pane, "info")
        udp_datagram = ntwk.recv(message)
        if udp.reassemble_message(udp_datagram) is not None:
            header, image_bytes = udp.reassemble_message(udp_datagram)
            dest_port = header[1]
            if dest_port == self.port_number:
                self.window.write_log(f"~ DVC: Message received from port {header[0]}...", self.pane, "success")
                with open(output_file_name, "wb") as f:
                    f.write(image_bytes)
                    self.window.write_log(f"~ DVC: Message successfully reassembled...", self.pane, "success")
            else:
                self.window.write_log(f"~ DVC: ERROR: Port unreachable")
        else:
            self.window.write_log(f"~ DVC: ERROR: datagram corrupted...", self.pane, "error")

    def get_port_number(self):
        return self.port_number
    
    def set_port_number(self, port_number):
        self.port_number = port_number

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name