import udp_datagram as udp
import network_layer as ntwk
import time
import ipaddress

class Device():
    '''
    Represents a device that can send and receive messages using UDP.
    '''
    def __init__(self, port_number, ip_address = ipaddress.IPv4Address("127.0.0.1"), name = "Unnamed_Device"):
        self.port_number = port_number
        self.ip_address = ip_address
        self.name = name



    def send_message(self, dest_port, payload, corrupt_chance = 0):
        '''
        Sends a message to the specified destination port with the given payload.
        The message may be corrupted with the specified chance.
        '''

        udp_datagram = udp.create_message(self.port_number, dest_port, payload)
        print(f"DVC: {self.name} is sending a message...")
        return (ntwk.send(udp_datagram, corrupt_chance))



    def receive_message(self, message, output_file_name):
        '''
        Receives a message and reassembles it into the original payload.
        The reassembled payload is saved to the specified output file name.
        '''
        
        print(f"DVC: {self.name} is receiving a message...")
        udp_datagram = ntwk.recv(message)
        if udp.reassemble_message(udp_datagram) is not None:
            header, image_bytes = udp.reassemble_message(udp_datagram)
            print("src_port: ", header[0])
            print("dest_port: ", header[1])
            print("payload_length: ", header[2])
            print("checksum: ", header[3])
            with open(output_file_name, "wb") as f:
                f.write(image_bytes)
            print(f"DVC: {self.name} received the message: {output_file_name}.")
        else:
            print(f"DVC: {self.name} did not received the message (it was probably corrupted).")



    def get_port_number(self):
        return self.port_number
    
    def set_port_number(self, port_number):
        self.port_number = port_number

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name