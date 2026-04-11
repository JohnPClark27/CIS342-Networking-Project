

class Device():
    def __init__(self, port_number, name, pane, protocol, worker):
        self.port_number = port_number
        self.name = name
        self.pane = pane
        self.protocol = protocol
        self.worker = worker

    def send_message(self, dest_port, payload_bytes, network_layer):
        self.worker.log_signal.emit("~ DVC: Segmenting payload", self.pane, "info")
        segments = self.protocol.segment(self.port_number, dest_port, payload_bytes)
        self.protocol.send(segments, network_layer)
        self.worker.log_signal.emit("~ DVC: Segments transmitted", self.pane, "info")

    def receive_message(self, output_file_name):
        buffer = bytearray()
        self.worker.log_signal.emit("~ DVC: Receiving file", self.pane, "info")
        while True:
            result = self.protocol.receive()
            if result == "END":
                self.worker.log_signal.emit("~ DVC: End of file received", self.pane, "info")
                break
            elif result is None:
                self.worker.log_signal.emit("~ DVC: Segment dropped or corrupted...", self.pane, "error")
            else:
                header, payload = result
                if header[1] == self.port_number:
                    self.worker.log_signal.emit("~ DVC: Segment received", self.pane, "info")
                    buffer.extend(payload)

        with open(output_file_name, "wb") as f:
            f.write(buffer)
        self.worker.log_signal.emit("~ DVC: File successfully assembled", self.pane, "info")
        return output_file_name
