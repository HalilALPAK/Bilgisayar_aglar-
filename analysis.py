import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

def plot_results(results_df, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.bar(results_df['Loss Rate'].astype(str), results_df[ylabel])
    plt.title(title)
    plt.xlabel('Loss Rate (%)')
    plt.ylabel(ylabel)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(filename)
    plt.close()
    print(f"Saved plot: {filename}")

def analyze_log(filename):
    if not os.path.exists(filename):
        print(f"Log file {filename} not found.")
        return

    df = pd.read_csv(filename)
    
    # Filter by events
    send_data = df[(df['event'] == 'SEND') & (df['type'] == 'DATA')]
    recv_ack = df[(df['event'] == 'RECV') & (df['type'] == 'ACK')]
    timeouts = df[df['event'] == 'TIMEOUT']
    
    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()
    duration = end_time - start_time
    
    total_bytes_sent = send_data['payload_size'].sum()
    unique_packets = send_data['seq_num'].nunique()
    unique_bytes = send_data.drop_duplicates(subset=['seq_num'])['payload_size'].sum()
    
    throughput = (total_bytes_sent * 8) / duration if duration > 0 else 0 # bps
    goodput = (unique_bytes * 8) / duration if duration > 0 else 0 # bps
    
    retransmission_rate = (len(send_data) - unique_packets) / unique_packets if unique_packets > 0 else 0
    
    print(f"Analysis for {filename}:")
    print(f"-----------------------------------")
    print(f"Total Duration:      {duration:.2f} s")
    print(f"Total Bytes Sent:    {total_bytes_sent} bytes")
    print(f"Unique Bytes:        {unique_bytes} bytes")
    print(f"Throughput:          {throughput/1000:.2f} kbps")
    print(f"Goodput:             {goodput/1000:.2f} kbps")
    print(f"Retransmission Rate: {retransmission_rate*100:.2f}%")
    print(f"Total Timeouts:      {len(timeouts)}")
    print(f"-----------------------------------")
    
    return {
        'Filename': filename,
        'Loss Rate': float(filename.split('_loss_')[1].split('_')[0]) * 100,
        'Duration (s)': duration,
        'Throughput (kbps)': throughput / 1000,
        'Goodput (kbps)': goodput / 1000,
        'Retransmission Rate (%)': retransmission_rate * 100,
        'Timeouts': len(timeouts)
    }

def run_full_analysis():
    logs = [f for f in os.listdir('.') if f.startswith('log_loss_') and f.endswith('.csv')]
    if not logs:
        print("No logs found.")
        return

    all_results = []
    for log in sorted(logs):
        res = analyze_log(log)
        if res:
            all_results.append(res)
    
    df = pd.DataFrame(all_results)
    
    # Generate plots
    plot_results(df, 'Throughput vs Loss Rate', 'Throughput (kbps)', 'throughput_vs_loss.png')
    plot_results(df, 'Goodput vs Loss Rate', 'Goodput (kbps)', 'goodput_vs_loss.png')
    plot_results(df, 'Retransmission Rate vs Loss Rate', 'Retransmission Rate (%)', 'retransmission_vs_loss.png')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_log(sys.argv[1])
    else:
        run_full_analysis()
