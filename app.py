import udp_datagram as udp
import network_layer as ntwk
import device

src_port = int(input(f"Enter source port number: "))
dest_port = int(input(f"Enter destination port number: "))
payload = input(f"Enter text or name of file to send: ") # using "udp_segment_structure.png"
corrupt_chance = float(input("Enter chance of corruption (0-100): ")) / 100

# message = udp.create_message(src_port, dest_port, payload)
# udp.reassemble_message(message)

Device_A = device.Device(src_port)
Device_B = device.Device(dest_port)

message = Device_A.send_message(dest_port, payload, corrupt_chance)
Device_B.receive_message(message, "reassembled.png")