"""
This file contains the SenderWorker and ReceiverWorker classes, which are QThreads responsible for sending and receiving messages in the background without freezing the GUI. They use the Device class to perform the actual sending and receiving of messages, and they emit signals to update the GUI with logs and images as needed.
"""

from PySide6.QtCore import QThread, Signal
from device import Device
import os

class SenderWorker(QThread):
    log_signal = Signal(str,str,str)

    def __init__(self, src_port, dest_port, ip_address, dest_ip_address, name, pane, file_path, protocol):
        super().__init__()
        self.port_a = src_port
        self.port_b = dest_port
        self.ip_address = ip_address
        self.dest_ip_address = dest_ip_address
        self.name = name
        self.pane = pane
        self.file_path = file_path
        self.protocol = protocol

    def run(self):
        device1 = Device(self.port_a, self.ip_address, self.name, self.pane, self.protocol, self)
        device1.send_message(self.dest_ip_address, self.port_b, self.file_path)

class ReceiverWorker(QThread):
    log_signal = Signal(str, str, str)
    image_signal = Signal(str)

    def __init__(self, port, ip_address, name, pane, output_file_name, protocol, sender_ip=None, sender_port=None):
        super().__init__()
        self.port = port
        self.ip_address = ip_address
        self.name = name
        self.pane = pane
        self.output_file_name = output_file_name
        self.protocol = protocol
        self.sender_ip = sender_ip

    def run(self):
        device2 = Device(self.port, self.ip_address, self.name, self.pane, self.protocol, self)

        output = device2.receive_message(self.output_file_name, sender_ip=self.sender_ip)

        if os.path.exists(self.output_file_name):
            self.image_signal.emit(self.output_file_name)
        else:
            self.log_signal.emit("~ WRK: No output file found", self.pane, "error")