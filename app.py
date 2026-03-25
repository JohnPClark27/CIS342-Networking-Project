import device

src_port = int(input(f"Enter source port number: "))
dest_port = int(input(f"Enter destination port number: "))
payload = input(f"Enter text or name of file to send: ")
corrupt_chance = float(input("Enter chance of corruption (0-100): ")) / 100

Device_A = device.Device(src_port, "Device A")
Device_B = device.Device(dest_port, "Device B")

message = Device_A.send_message(dest_port, payload, corrupt_chance)
Device_B.receive_message(message, "reassembled.png")