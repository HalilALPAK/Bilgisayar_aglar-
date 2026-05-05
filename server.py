import socket
import os
import time
from packet import Packet, TYPE_START, TYPE_DATA, TYPE_END, TYPE_ACK

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
BUFFER_SIZE = 4096

def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}")

    expected_seq = 0
    file_data = {}
    total_packets = -1
    client_addr = None
    output_filename = "received_file"

    while True:
        print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
        expected_seq = 0
        file_data = {}
        total_packets = -1
        client_addr = None
        transfer_active = True

        while transfer_active:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            packet = Packet.unpack(data)

            if not packet:
                continue

            if packet.p_type == TYPE_START:
                print(f"Transfer started from {addr}")
                expected_seq = 0
                file_data = {}
                total_packets = packet.total_packets
                ack = Packet(TYPE_ACK, seq_num=packet.seq_num)
                sock.sendto(ack.pack(), addr)

            elif packet.p_type == TYPE_DATA:
                if packet.is_valid():
                    if packet.seq_num == expected_seq:
                        file_data[packet.seq_num] = packet.payload
                        expected_seq += 1
                        # ACK the current correctly received packet
                        ack = Packet(TYPE_ACK, seq_num=packet.seq_num)
                        sock.sendto(ack.pack(), addr)
                    else:
                        # Out of order or duplicate: re-ACK the last successful one
                        if expected_seq > 0:
                            ack = Packet(TYPE_ACK, seq_num=expected_seq - 1)
                            sock.sendto(ack.pack(), addr)
                        else:
                            # If we haven't even gotten seq 0, re-ACK START (seq 0) 
                            # Or just ignore until seq 0 arrives correctly.
                            pass

            elif packet.p_type == TYPE_END:
                print("Transfer completed.")
                ack = Packet(TYPE_ACK, seq_num=packet.seq_num)
                sock.sendto(ack.pack(), addr)
                
                # Save file
                with open(f"received_{int(time.time())}.bin", "wb") as f:
                    for i in range(len(file_data)):
                        f.write(file_data[i])
                transfer_active = False

    sock.close()

if __name__ == "__main__":
    run_server()
