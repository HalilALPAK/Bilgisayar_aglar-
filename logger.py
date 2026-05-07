import csv
import time
import os

class Logger:
    def __init__(self, filename="transfer_log.csv"):
        self.filename = filename
        self.header = ["timestamp", "event", "type", "seq_num", "payload_size"]
        
        # Initialize file with header
        with open(self.filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.header)

    def log(self, event, p_type, seq_num, payload_size=0):
        with open(self.filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), event, p_type, seq_num, payload_size])

# Global logger instance
logger = None

def init_logger(filename):
    global logger
    logger = Logger(filename)

def log_event(event, p_type, seq_num, payload_size=0):
    if logger:
        logger.log(event, p_type, seq_num, payload_size)
