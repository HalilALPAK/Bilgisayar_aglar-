import socket
import os
import time
import random
import argparse
import threading
from packet import Packet, TYPE_START, TYPE_DATA, TYPE_END, TYPE_ACK
from logger import init_logger, log_event

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
CHUNK_SIZE = 1024
TIMEOUT = 0.5
WINDOW_SIZE = 5
MAX_RETRIES = 5  # maximum retransmission attempts per packet

class GBNClient:
    def __init__(self, filename, loss_rate, timeout, window_size):
        self.filename = filename
        self.loss_rate = loss_rate
        self.timeout = timeout
        self.window_size = window_size
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1) # Short timeout for receiver loop
        self.addr = (SERVER_IP, SERVER_PORT)
        
        self.base = 0
        self.next_seq = 0
        self.timer_start = None
        self.lock = threading.Lock()
        self.transfer_complete = False
        self.retry_counts = {}   # per-packet retry counter
        self.failed_packets = 0

        init_logger(f"log_gbn_loss_{loss_rate}_win_{window_size}.csv")

    def simulate_send(self, data):
        if random.random() > self.loss_rate:
            self.sock.sendto(data, self.addr)

    def receiver_thread(self):
        while not self.transfer_complete:
            try:
                data, _ = self.sock.recvfrom(4096)
                ack = Packet.unpack(data)
                if ack and ack.p_type == TYPE_ACK:
                    with self.lock:
                        if ack.seq_num >= self.base:
                            print(f"ACK {ack.seq_num} received (Cumulative)")
                            log_event("RECV", "ACK", ack.seq_num)
                            self.base = ack.seq_num + 1
                            if self.base == self.next_seq:
                                self.timer_start = None # No outstanding packets
                            else:
                                self.timer_start = time.time() # Restart timer for new base
            except socket.timeout:
                continue

    def run(self):
        if not os.path.exists(self.filename):
            return

        with open(self.filename, "rb") as f:
            file_bytes = f.read()
        chunks = [file_bytes[i:i+CHUNK_SIZE] for i in range(0, len(file_bytes), CHUNK_SIZE)]
        total_packets = len(chunks)
        
        # START Phase
        start_packet = Packet(TYPE_START, seq_num=0, total_packets=total_packets)
        while True:
            try:
                self.sock.sendto(start_packet.pack(), self.addr)
                self.sock.settimeout(self.timeout)
                data, _ = self.sock.recvfrom(4096)
                ack = Packet.unpack(data)
                if ack and ack.p_type == TYPE_ACK and ack.seq_num == 0:
                    break
            except socket.timeout:
                continue

        # DATA Phase
        self.sock.settimeout(0.1)
        rec_t = threading.Thread(target=self.receiver_thread)
        rec_t.start()
        
        start_time = time.time()
        while self.base < total_packets:
            with self.lock:
                # Send packets in window
                while self.next_seq < self.base + self.window_size and self.next_seq < total_packets:
                    print(f"Sending Packet {self.next_seq}...")
                    log_event("SEND", "DATA", self.next_seq, len(chunks[self.next_seq]))
                    packet = Packet(TYPE_DATA, seq_num=self.next_seq, total_packets=total_packets, payload=chunks[self.next_seq])
                    self.simulate_send(packet.pack())
                    
                    if self.base == self.next_seq:
                        self.timer_start = time.time()
                    self.next_seq += 1
                
                # Check for timeout
                if self.timer_start and time.time() - self.timer_start > self.timeout:
                    self.retry_counts[self.base] = self.retry_counts.get(self.base, 0) + 1
                    if self.retry_counts[self.base] > MAX_RETRIES:
                        log_event("FAILED", "DATA", self.base)
                        print(f"Packet {self.base} FAILED after {MAX_RETRIES} retries. Advancing base.")
                        self.failed_packets += 1
                        self.base += 1
                        self.timer_start = time.time() if self.base < self.next_seq else None
                    else:
                        print(f"Timeout at base {self.base} (retry {self.retry_counts[self.base]}/{MAX_RETRIES}), retransmitting window...")
                        log_event("TIMEOUT", "DATA", self.base)
                        self.next_seq = self.base  # Go back to base
                        self.timer_start = time.time()
            
            time.sleep(0.01) # Small delay to prevent CPU hogging

        self.transfer_complete = True
        rec_t.join()

        # END Phase
        end_packet = Packet(TYPE_END, seq_num=total_packets)
        while True:
            try:
                self.sock.sendto(end_packet.pack(), self.addr)
                self.sock.settimeout(self.timeout)
                data, _ = self.sock.recvfrom(4096)
                ack = Packet.unpack(data)
                if ack and ack.p_type == TYPE_ACK and ack.seq_num == total_packets:
                    break
            except socket.timeout:
                continue

        end_time = time.time()
        print(f"Transfer finished in {end_time - start_time:.2f} seconds.")
        if self.failed_packets > 0:
            print(f"WARNING: {self.failed_packets} packet(s) could not be delivered after {MAX_RETRIES} retries.")

        import hashlib
        with open(self.filename, "rb") as f:
            original_md5 = hashlib.md5(f.read()).hexdigest()
        print(f"Original file MD5: {original_md5}")
        self.sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="donem_projesi.pdf")
    parser.add_argument("--loss", type=float, default=0.1)
    parser.add_argument("--timeout", type=float, default=0.5)
    parser.add_argument("--window", type=int, default=5)
    args = parser.parse_args()
    
    client = GBNClient(args.file, args.loss, args.timeout, args.window)
    client.run()
