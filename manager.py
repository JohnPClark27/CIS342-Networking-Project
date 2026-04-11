import sys, os, ipaddress
import device
from PySide6.QtWidgets import QApplication
from gui import MainWindow
import ipaddress as ipa
import network_layer
from udp_protocol import UdpProtocol
from worker import SenderWorker, ReceiverWorker
import queue

class Manager:
    '''
    Manages the overall application, including the GUI and the devices.
    '''
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.window = MainWindow()
        
        self.selected_source_image = None
        self.corruption_chance = 0
        self.protocol = "UDP"

        self.connect_signals()
        self.sender = None
        self.receiver = None

    def connect_signals(self):
        self.window.ui.send_file_btn.clicked.connect(self.on_send)
        self.window.ui.protocol_combo.currentTextChanged.connect(self.change_protocol)
        self.window.ui.select_file_btn.clicked.connect(self.select_file)
        self.window.ui.corruption_slider.valueChanged.connect(self.set_corruption_chance)

    def change_protocol(self, protocol_name):
        self.protocol = protocol_name
        self.window.write_log(f"~ SYS: Protocol switched to {protocol_name}", "left", "info")

    def select_file(self):
        self.selected_source_image = self.window.open_file()
        if self.selected_source_image:
            self.window.write_log(f"~ SYS: Image loaded: {self.selected_source_image}", "left", "success")
        else:
            self.window.write_log(f"~ SYS: Error: No file selected.", "left", "error")

    def set_corruption_chance(self, value):
        self.corruption_chance = value
        self.window.update_corruption_label(value)



    def on_send(self):
        '''
        Handles the send button click event. It prepares the devices and simulates sending a message from Device A to Device B.
        '''
        output_file_name = "received_image.png"


        # Delete output file if it already exists so it doesn't interfere with the next transmission
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
            print(f"SYS: File '{output_file_name}' has been deleted.")
        else:
            print(f"SYS: File '{output_file_name}' does not exist.")

        # Ensure input file exists
        if self.selected_source_image is None:
            self.window.write_log("~ SYS: ERROR: No file selected.", "left", "error")
            return

        # Read port numbers and IP addresses from the GUI
        portNumberA = int(self.window.ui.sender_port_input.text().strip())
        dest_port = int(self.window.ui.dest_port_input.text().strip())
        portNumberB = int(self.window.ui.receiver_port_input.text().strip())

        ipAddressA = ipa.IPv4Address(self.window.ui.ip_input.text().strip())
        ipAddressB = ipa.IPv4Address(self.window.ui.rec_ip_input.text().strip())

        a_to_b = queue.Queue()
        b_to_a = queue.Queue()
        self.sender = SenderWorker(portNumberA, portNumberB, "Device1", "left", network_layer = network_layer, file_path=self.selected_source_image)
        self.receiver = ReceiverWorker(portNumberB, "Device2", "right", output_file_name=output_file_name)
        protocol_a = UdpProtocol(worker = self.sender,pane = "left", a_to_b=a_to_b, b_to_a = b_to_a,corrupt_chance=self.corruption_chance, drop_chance=0)
        protocol_b = UdpProtocol(worker=self.receiver,pane = "right", a_to_b=a_to_b, b_to_a = b_to_a, corrupt_chance=self.corruption_chance, drop_chance=0)

        self.sender.set_protocol(protocol_a)
        self.receiver.set_protocol(protocol_b)

        self.sender.log_signal.connect(self.window.write_log)
        self.receiver.log_signal.connect(self.window.write_log)
        self.receiver.image_signal.connect(self.window.set_received_image)

        self.receiver.start()
        self.sender.start()

if __name__ == "__main__":
    manager = Manager()
    manager.window.show()
    sys.exit(manager.app.exec())