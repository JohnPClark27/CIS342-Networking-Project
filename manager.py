import sys, os
from PySide6.QtWidgets import QApplication
from gui import MainWindow
from PySide6.QtGui import (QPixmap, QIcon, QRegularExpressionValidator)
import ipaddress as ipa
from worker import SenderWorker, ReceiverWorker
import config
import network_layer as ntwk

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
        self.protocol = "UDP" # default protocol is UDP, but can be changed in the GUI

        self.connect_signals()
        self.sender = None
        self.receiver = None
        self.window.closeEvent = self._on_window_close

    def _on_window_close(self, event):
        '''Handle cleanup before window closes.'''
        try:
            self.stop_threads()
        except:
            pass
        # Call the original closeEvent
        from gui import MainWindow
        MainWindow.closeEvent(self.window, event)

    def connect_signals(self):
        self.window.ui.send_file_btn.clicked.connect(self.on_send)
        self.window.ui.protocol_combo.currentTextChanged.connect(self.change_protocol)
        self.window.ui.select_file_btn.clicked.connect(self.select_file)
        self.window.ui.corruption_slider.valueChanged.connect(self.set_corruption_chance)
        self.window.ui.drop_slider.valueChanged.connect(self.set_drop_chance)
        self.window.ui.delay_slider.valueChanged.connect(self.set_delay_from_gui)
        self.window.ui.clear_all_btn.clicked.disconnect()
        self.window.ui.clear_all_btn.clicked.connect(self.manager_clear_all)

    def stop_threads(self):
        """Safely shuts down running QThreads using cooperative cancellation."""
        import network_layer as ntwk # Ensure this is imported at the top of manager.py

        # 1. Ask threads politely to stop and feed poison pills
        if self.receiver and self.receiver.isRunning():
            self.receiver.requestInterruption()
            dest_device = ntwk.devices.get((str(self.receiver.ip_address), self.receiver.port))
            if dest_device:
                dest_device.buffer.put(b"STOP")

        if self.sender and self.sender.isRunning():
            self.sender.requestInterruption()
            src_device = ntwk.devices.get((str(self.sender.ip_address), self.sender.port_a))
            if src_device:
                src_device.buffer.put(b"STOP") # Breaks sender out of ACK waiting

        # 2. Give them a fraction of a second to shut themselves down
        if self.receiver and self.receiver.isRunning():
            self.receiver.wait(300)
        if self.sender and self.sender.isRunning():
            self.sender.wait(300)

        # 3. Only forcefully terminate if they are completely unresponsive
        if self.receiver and self.receiver.isRunning():
            self.receiver.terminate()
        if self.sender and self.sender.isRunning():
            self.sender.terminate()
            
    def change_protocol(self, protocol_name):
        self.protocol = protocol_name
        self.window.write_log(f"~ SYS: Protocol set to {protocol_name}", "left", "info")

    def select_file(self):
        self.selected_source_image = self.window.open_file()
        if self.selected_source_image:
            self.window.write_log(f"~ SYS: Image loaded: {self.selected_source_image}", "left", "success")
        else:
            self.window.write_log(f"~ SYS: Error: No file selected.", "left", "error")

    def set_corruption_chance(self, value):
        config.corruption_chance = value
        self.window.update_corruption_label(value)

    def set_drop_chance(self, value):
        config.drop_chance = value
        self.window.update_drop_label(value)

    def set_delay(self, value):
        config.delay = value
        self.window.update_delay_label(value)

    def manager_clear_all(self):
        """Kills threads first, then wipes the GUI so no stray logs appear."""
        self.stop_threads()     
        self.window.clear_all()

    def set_delay_from_gui(self, value):

        '''Converts milliseconds to seconds and sets the delay.'''
        delay_in_seconds = value / 1000.0
        self.set_delay(delay_in_seconds)
        self.window.update_delay_display(value)
    
    def on_send(self):
        '''
        Handles the send button click event. It prepares the devices and simulates sending a message from Device A to Device B.
        '''
        output_file_name = "received_image.png"

        # Delete output file if it already exists so it doesn't interfere with the next transmission
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
            print(f"SYS: File '{output_file_name}' has been deleted for the next transmission.")

        # Ensure input file exists
        if self.selected_source_image is None:
            self.window.write_log("~ SYS: ERROR: No file selected.", "left", "error")
            return
        self.stop_threads() 
        # Read port numbers and IP addresses from the GUI
        portNumberA = int(self.window.ui.sender_port_input.text().strip())
        dest_port = int(self.window.ui.dest_port_input.text().strip())
        portNumberB = int(self.window.ui.receiver_port_input.text().strip())
        
        ipAddressA = ipa.IPv4Address(self.window.ui.ip_input.text().strip())
        ipAddressB = ipa.IPv4Address(self.window.ui.rec_ip_input.text().strip())

        # Create sender and receiver devices, set their protocols, and connect their signals to the GUI
        self.sender = SenderWorker(
            src_port=portNumberA,
            dest_port=dest_port,
            ip_address=ipAddressA,
            dest_ip_address=ipAddressB,
            name="Device1",
            pane="left",
            file_path=self.selected_source_image,
            protocol=self.protocol
        )
        self.receiver = ReceiverWorker(
            port=portNumberB,
            ip_address=ipAddressB,
            name="Device2",
            pane="right",
            output_file_name=output_file_name,
            protocol=self.protocol,
            sender_ip=ipAddressA,
        )

        self.sender.log_signal.connect(self.window.write_log)
        self.receiver.log_signal.connect(self.window.write_log)
        self.receiver.image_signal.connect(self.window.set_received_image)

        # Start the sender and receiver threads
        self.receiver.start()
        self.sender.start()



if __name__ == "__main__":
    manager = Manager()
    manager.window.show()
    sys.exit(manager.app.exec())
