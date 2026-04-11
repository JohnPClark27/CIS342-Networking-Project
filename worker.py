from PySide6.QtCore import QThread, Signal
from device import Device
import os

class SenderWorker(QThread):
    log_signal = Signal(str,str,str)

    def __init__(self, port_a,port_b, name, pane, network_layer, file_path):
        super().__init__()
        self.port_a = port_a
        self.port_b = port_b
        self.name = name
        self.pane = pane
        self.network_layer = network_layer
        self.file_path = file_path
        self.protocol = None

    def set_protocol(self, protocol):
        self.protocol = protocol

    def run(self):
        with open(self.file_path, "rb") as file:
            payload_bytes = file.read()

        device1 = Device(self.port_a, self.name, self.pane, self.protocol, self)

        device1.send_message(self.port_b, payload_bytes, self.network_layer)

class ReceiverWorker(QThread):
    log_signal = Signal(str, str, str)
    image_signal = Signal(str)

    def __init__(self, port_b, name, pane, output_file_name):
        super().__init__()
        self.port_b = port_b
        self.name = name
        self.pane = pane
        self.output_file_name = output_file_name
        self.protocol = None

    def set_protocol(self, protocol):
        self.protocol = protocol

    def run(self):
        device2 = Device(self.port_b, self.name, self.pane, self.protocol, self)

        output = device2.receive_message(self.output_file_name)

        if os.path.exists(self.output_file_name):
            self.image_signal.emit(self.output_file_name)
        else:
            self.log_signal.emit("~ WRK: No output file found", self.pane, "error")