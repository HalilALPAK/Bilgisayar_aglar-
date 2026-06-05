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

def plot_comparison(sw_df, gbn_df, ylabel, title, filename):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(sw_df))
    width = 0.35
    bars1 = ax.bar([i - width/2 for i in x], sw_df[ylabel], width, label='Stop-and-Wait')
    bars2 = ax.bar([i + width/2 for i in x], gbn_df[ylabel].reindex(sw_df.index, fill_value=0), width, label='Go-Back-N')
    ax.set_title(title)
    ax.set_xlabel('Loss Rate (%)')
    ax.set_ylabel(ylabel)
    ax.set_xticks(list(x))
    ax.set_xticklabels(sw_df['Loss Rate'].astype(str).tolist())
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Saved comparison plot: {filename}")

def analyze_log(filename):
    if not os.path.exists(filename):
        print(f"Log file {filename} not found.")
        return None

    df = pd.read_csv(filename)

    send_data = df[(df['event'] == 'SEND') & (df['type'] == 'DATA')]
    recv_ack = df[(df['event'] == 'RECV') & (df['type'] == 'ACK')]
    timeouts = df[df['event'] == 'TIMEOUT']
    failed = df[df['event'] == 'FAILED']

    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()
    duration = end_time - start_time

    total_bytes_sent = send_data['payload_size'].sum()
    unique_packets = send_data['seq_num'].nunique()
    unique_bytes = send_data.drop_duplicates(subset=['seq_num'])['payload_size'].sum()

    # RTT estimation: average time between SEND DATA and matching RECV ACK
    rtt_values = []
    for seq, group in send_data.groupby('seq_num'):
        ack_times = recv_ack[recv_ack['seq_num'] == seq]['timestamp']
        send_time = group['timestamp'].min()
        if not ack_times.empty:
            first_ack = ack_times.min()
            if first_ack > send_time:
                rtt_values.append(first_ack - send_time)
    avg_rtt_ms = (sum(rtt_values) / len(rtt_values) * 1000) if rtt_values else 0

    throughput = (total_bytes_sent * 8) / duration if duration > 0 else 0  # bps
    goodput = (unique_bytes * 8) / duration if duration > 0 else 0  # bps
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
    print(f"Failed Packets:      {len(failed)}")
    print(f"Avg RTT:             {avg_rtt_ms:.2f} ms")
    print(f"-----------------------------------")

    # Parse loss rate from filename
    try:
        loss_rate = float(filename.split('_loss_')[1].split('_')[0]) * 100
    except (IndexError, ValueError):
        loss_rate = 0.0

    return {
        'Filename': filename,
        'Loss Rate': loss_rate,
        'Duration (s)': duration,
        'Throughput (kbps)': throughput / 1000,
        'Goodput (kbps)': goodput / 1000,
        'Retransmission Rate (%)': retransmission_rate * 100,
        'Timeouts': len(timeouts),
        'Failed Packets': len(failed),
        'Avg RTT (ms)': avg_rtt_ms,
    }

def run_full_analysis():
    sw_logs = sorted([f for f in os.listdir('.') if f.startswith('log_loss_') and f.endswith('.csv')])
    gbn_logs = sorted([f for f in os.listdir('.') if f.startswith('log_gbn_') and f.endswith('.csv')])

    if not sw_logs and not gbn_logs:
        print("No log files found.")
        return

    sw_results = []
    for log in sw_logs:
        res = analyze_log(log)
        if res:
            sw_results.append(res)

    gbn_results = []
    for log in gbn_logs:
        res = analyze_log(log)
        if res:
            gbn_results.append(res)

    # Stop-and-Wait plots
    if sw_results:
        df = pd.DataFrame(sw_results).sort_values('Loss Rate')
        plot_results(df, 'Throughput vs Loss Rate (Stop-and-Wait)', 'Throughput (kbps)', 'throughput_vs_loss.png')
        plot_results(df, 'Goodput vs Loss Rate (Stop-and-Wait)', 'Goodput (kbps)', 'goodput_vs_loss.png')
        plot_results(df, 'Retransmission Rate vs Loss Rate (Stop-and-Wait)', 'Retransmission Rate (%)', 'retransmission_vs_loss.png')

    # GBN plots
    if gbn_results:
        gbn_df = pd.DataFrame(gbn_results).sort_values('Loss Rate')
        plot_results(gbn_df, 'Throughput vs Loss Rate (Go-Back-N)', 'Throughput (kbps)', 'throughput_vs_loss_gbn.png')
        plot_results(gbn_df, 'Goodput vs Loss Rate (Go-Back-N)', 'Goodput (kbps)', 'goodput_vs_loss_gbn.png')

    # Comparison plots (S&W vs GBN)
    if sw_results and gbn_results:
        sw_df = pd.DataFrame(sw_results).sort_values('Loss Rate').reset_index(drop=True)
        gbn_df = pd.DataFrame(gbn_results).sort_values('Loss Rate').reset_index(drop=True)
        plot_comparison(sw_df, gbn_df, 'Throughput (kbps)',
                        'Throughput Comparison: Stop-and-Wait vs Go-Back-N', 'comparison_throughput.png')
        plot_comparison(sw_df, gbn_df, 'Goodput (kbps)',
                        'Goodput Comparison: Stop-and-Wait vs Go-Back-N', 'comparison_goodput.png')
        plot_comparison(sw_df, gbn_df, 'Retransmission Rate (%)',
                        'Retransmission Rate Comparison: S&W vs GBN', 'comparison_retransmission.png')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_log(sys.argv[1])
    else:
        run_full_analysis()
