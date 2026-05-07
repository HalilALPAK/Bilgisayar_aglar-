import struct
import hashlib

# Packet Types
TYPE_START = 0
TYPE_DATA  = 1
TYPE_ACK   = 2
TYPE_END   = 3

# Header Formats
# DATA: Type(B), SeqNum(I), TotalPackets(I), PayloadLen(H), Checksum(16s) = 1+4+4+2+16 = 27 bytes
DATA_HEADER_FMT = "!BIIH16s"
DATA_HEADER_SIZE = struct.calcsize(DATA_HEADER_FMT)

# ACK: Type(B), AckNum(I), Checksum(16s) = 1+4+16 = 21 bytes
ACK_HEADER_FMT = "!BI16s"
ACK_HEADER_SIZE = struct.calcsize(ACK_HEADER_FMT)

def calculate_checksum(data):
    """Calculate MD5 checksum of the data."""
    return hashlib.md5(data).digest()

class Packet:
    def __init__(self, p_type, seq_num=0, total_packets=0, payload=b""):
        self.p_type = p_type
        self.seq_num = seq_num
        self.total_packets = total_packets
        self.payload = payload
        self.checksum = calculate_checksum(payload)

    def pack(self):
        if self.p_type == TYPE_ACK:
            header = struct.pack(ACK_HEADER_FMT, self.p_type, self.seq_num, self.checksum)
            return header
        else:
            header = struct.pack(DATA_HEADER_FMT, self.p_type, self.seq_num, self.total_packets, len(self.payload), self.checksum)
            return header + self.payload

    @staticmethod
    def unpack(data):
        if not data:
            return None
        
        p_type = data[0]
        if p_type == TYPE_ACK:
            if len(data) < ACK_HEADER_SIZE: return None
            p_type, ack_num, checksum = struct.unpack(ACK_HEADER_FMT, data[:ACK_HEADER_SIZE])
            return Packet(p_type, seq_num=ack_num, payload=b"") # Checksum stored but not re-calculated for ACK usually
        else:
            if len(data) < DATA_HEADER_SIZE: return None
            p_type, seq_num, total_packets, p_len, checksum = struct.unpack(DATA_HEADER_FMT, data[:DATA_HEADER_SIZE])
            payload = data[DATA_HEADER_SIZE:DATA_HEADER_SIZE+p_len]
            packet = Packet(p_type, seq_num, total_packets, payload)
            packet.checksum = checksum
            return packet

    def is_valid(self):
        """Verify the payload against the checksum."""
        return calculate_checksum(self.payload) == self.checksum
