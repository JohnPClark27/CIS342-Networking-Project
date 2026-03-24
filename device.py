import udp_datagram as udp
import network_layer as ntwk
import random
import struct

class Device():
    def __init__(self, port_number):
        self.port_number = port_number

    def send_message(self, dest_port, payload, corrupt_chance = 0):
        message = udp.create_message(self.port_number, dest_port, payload)
        return (ntwk.send(message, corrupt_chance))

    def receive_message(self, message, output_file_name):
        udp.reassemble_message(message, output_file_name)

    def get_port_number(self):
        return self.port_number
    