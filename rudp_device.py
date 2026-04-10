import rudp_datagram as rudp
import network_layer as ntwk
import time
import ipaddress
from gui import MainWindow
from device import Device

class RudpDevice(Device):
    '''
    Represents a device that can send and receive messages using UDP.
    '''

    def send_message(self, dest_port, payload, corrupt_chance = 0):
        self.window.write_log(f"~ DVC: Preparing message...", self.pane, "info")
        rudp_datagram = rudp.create_message(self.port_number, dest_port, payload)
        pass

    def receive_message(self, segment, output_file_name):
        pass

    def process_ack(self, ack_segment):
        pass