# Reliable UDP File Transfer Protocol

This project implements a reliable file transfer protocol over UDP, featuring sequence numbering, acknowledgments (ACKs), timeouts, and retransmissions. It includes both a "Stop-and-Wait" implementation and a "Go-Back-N" (Sliding Window) implementation.

## Project Structure

- `packet.py`: Defines the custom protocol header and packet structure (Type, SeqNum, Checksum, etc.).
- `server.py`: The UDP server that receives files and verifies integrity using MD5.
- `client.py`: Stop-and-Wait client with artificial loss simulation.
- `client_gbn.py`: Go-Back-N (Sliding Window) client with artificial loss simulation.
- `logger.py`: Logging utility to record events to CSV for performance analysis.
- `analysis.py`: Script to analyze logs and generate performance charts (Throughput, Goodput, etc.).

## Requirements

- Python 3.x
- pandas
- matplotlib

Install dependencies:
```bash
pip install pandas matplotlib
```

## How to Run

1. **Start the Server:**
   ```bash
   python server.py
   ```

2. **Run the Client (Stop-and-Wait):**
   ```bash
   python client.py --loss 0.1 --timeout 0.5
   ```

3. **Run the Client (Go-Back-N):**
   ```bash
   python client_gbn.py --loss 0.1 --window 5
   ```

4. **Analyze Results:**
   ```bash
   python analysis.py
   ```
   This will process the CSV logs and generate `.png` plots in the current directory.

## Performance Metrics

The system tracks:
- **Throughput**: Total bits sent per second.
- **Goodput**: Unique bits (successfully delivered) per second.
- **Completion Time**: Total time for transfer.
- **Retransmission Rate**: Ratio of duplicate packets to unique packets.

## Authors
- [User Name/ID]
