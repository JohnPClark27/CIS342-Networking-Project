import struct
import queue

HEADER_FORMAT = '!HHHH'
CHUNK_SIZE = 1024

class UdpProtocol():
    def __init__(self, worker, pane, a_to_b, b_to_a,corrupt_chance = 0, drop_chance = 0):

        self.worker = worker
        self.pane = pane # Left device A; Right device B
        self.a_to_b = a_to_b
        self.b_to_a = b_to_a
        self.corrupt_chance = corrupt_chance
        self.drop_chance = drop_chance

    def make_checksum(self, data: bytes) -> int:
        return sum(data) % 65535

    def segment(self, src_port, dest_port, payload_bytes):
        chunks = [payload_bytes[i:i+CHUNK_SIZE] for i in range(0, len(payload_bytes), CHUNK_SIZE)]
        segments = []
        for chunk in chunks:
            segments.append(self.create_segment(src_port, dest_port, chunk))

        return segments


    def create_segment(self, src_port, dest_port, chunk):
        length = 8 + len(chunk)

        temp_segment = struct.pack(HEADER_FORMAT, src_port, dest_port, length, 0) + chunk
        checksum = self.make_checksum(temp_segment)

        segment = struct.pack(HEADER_FORMAT, src_port, dest_port, length, checksum) + chunk
        return segment

    def receive(self):
        try:
            raw_segment = self.a_to_b.get(timeout=5.0)
        except queue.Empty:
            return None

        if raw_segment == "END":
            return "END"

        header = struct.unpack(HEADER_FORMAT, raw_segment[:8])
        payload = raw_segment[8:]

        src_port = header[0]
        dest_port = header[1]
        payload_bytes = header[2]
        checksum = header[3]

        temp_segment = struct.pack(HEADER_FORMAT, src_port, dest_port, payload_bytes, 0) + payload
        temp_checksum = self.make_checksum(temp_segment)

        if temp_checksum != checksum:
            return None
        else:
            return header, payload


    def send(self, segments, network_layer):
        for i, seg in enumerate(segments):
            self.worker.log_signal.emit(f"~ UDP: Sending segment {i+1}/{len(segments)}", self.pane, "info")
            network_layer.send(seg, self.a_to_b, self.corrupt_chance, self.drop_chance)
        self.a_to_b.put("END")
