import socket
import os
import time
import random
import argparse
from packet import Packet, TYPE_START, TYPE_DATA, TYPE_END, TYPE_ACK
from logger import init_logger, log_event

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
CHUNK_SIZE = 1024
TIMEOUT = 0.5 # seconds
LOSS_RATE = 0.1 # 10% artificial loss

def simulate_send(sock, data, addr, loss_rate):
    if random.random() > loss_rate:
        sock.sendto(data, addr)
    else:
        pass # Simulate packet loss

def run_client(filename, loss_rate, timeout):
    init_logger(f"log_loss_{loss_rate}_timeout_{timeout}.csv")
    
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    addr = (SERVER_IP, SERVER_PORT)

    # Read file and chunk it
    with open(filename, "rb") as f:
        file_bytes = f.read()
    
    chunks = [file_bytes[i:i+CHUNK_SIZE] for i in range(0, len(file_bytes), CHUNK_SIZE)]
    total_packets = len(chunks)
    print(f"File read: {len(file_bytes)} bytes, {total_packets} chunks.")

    # Phase 1: START
    start_packet = Packet(TYPE_START, seq_num=0, total_packets=total_packets)
    while True:
        try:
            print("Sending START...")
            log_event("SEND", "START", 0)
            simulate_send(sock, start_packet.pack(), addr, 0) # Don't lose START for now
            data, _ = sock.recvfrom(4096)
            ack = Packet.unpack(data)
            if ack and ack.p_type == TYPE_ACK and ack.seq_num == 0:
                log_event("RECV", "ACK", 0)
                print("START ACKed.")
                break
        except socket.timeout:
            log_event("TIMEOUT", "START", 0)
            continue

    # Phase 2: DATA (Stop-and-Wait)
    start_time = time.time()
    for seq, chunk in enumerate(chunks):
        packet = Packet(TYPE_DATA, seq_num=seq, total_packets=total_packets, payload=chunk)
        
        while True:
            try:
                print(f"Sending Packet {seq}...")
                log_event("SEND", "DATA", seq, len(chunk))
                simulate_send(sock, packet.pack(), addr, loss_rate)
                
                data, _ = sock.recvfrom(4096)
                ack = Packet.unpack(data)
                if ack and ack.p_type == TYPE_ACK and ack.seq_num == seq:
                    log_event("RECV", "ACK", seq)
                    print(f"ACK {seq} received.")
                    break
            except socket.timeout:
                log_event("TIMEOUT", "DATA", seq)
                print(f"Timeout for Packet {seq}, retransmitting...")
                continue

    # Phase 3: END
    end_packet = Packet(TYPE_END, seq_num=total_packets)
    while True:
        try:
            print("Sending END...")
            log_event("SEND", "END", total_packets)
            simulate_send(sock, end_packet.pack(), addr, 0)
            data, _ = sock.recvfrom(4096)
            ack = Packet.unpack(data)
            if ack and ack.p_type == TYPE_ACK and ack.seq_num == total_packets:
                log_event("RECV", "ACK", total_packets)
                print("END ACKed.")
                break
        except socket.timeout:
            log_event("TIMEOUT", "END", total_packets)
            continue

    end_time = time.time()
    print(f"Transfer finished in {end_time - start_time:.2f} seconds.")
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="donem_projesi.pdf")
    parser.add_argument("--loss", type=float, default=0.1)
    parser.add_argument("--timeout", type=float, default=0.5)
    args = parser.parse_args()
    
    run_client(args.file, args.loss, args.timeout)
