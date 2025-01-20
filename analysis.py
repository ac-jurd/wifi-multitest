import os
import re
import matplotlib.pyplot as plt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

USE_GRAPHIC = True
try:
    import matplotlib.pyplot as plt
except ImportError as e:
    if USE_GRAPHIC:
        raise e

# List of colors for bars
BAR_COLORS = ['#1f78ed', '#FF7F0E', '#2CA02C']  # We'll use these 3 colors for each subplot

def extract_data(content, filename):
    """Extract data from the content of a speedtest file."""
    try:
        ssid = re.search(r'speedtest-(.+)\.txt', filename).group(1)
        provider = re.search(r'Testing from (.*?) \(', content).group(1)
        best_server = re.search(r'Hosted by (.*?) \(', content).group(1)
        distance_km = re.search(r'\[(.*?) km\]', content).group(1)
        ping_ms = re.search(r'\[(.*?) km\]: ([\d\.]+) ms', content).group(2)
        download_speed_ms = re.search(r'Download: ([\d\.]+) Mbit/s', content).group(1)
        upload_speed_ms = re.search(r'Upload: ([\d\.]+) Mbit/s', content).group(1)

    except AttributeError as e:
        logging.error(f"Error parsing {filename}: {e}")
        return None  # Skip the file if any data is missing

    return {
        'ssid': ssid,
        'provider': provider,
        'best_server': best_server,
        'distance_km': distance_km,
        'ping_ms': ping_ms,
        'download_speed_ms': download_speed_ms,
        'upload_speed_ms': upload_speed_ms
    }

def read_speedtest_files(directory):
    """Reads all speedtest files in a directory."""
    speedtest_files = [
        filename for filename in os.listdir(directory)
        if filename.startswith('speedtest-') and filename.endswith('.txt')
    ]
    return speedtest_files

# Collect speedtest files
speedtest_files = read_speedtest_files(".")

# Extract data from files
data = []
for filename in speedtest_files:
    with open(filename, 'r') as file:
        content = file.read()
        result = extract_data(content, filename)
        if result:  # Only append valid data
            data.append(result)

# Sort data by download speed in descending order, ensuring no None or empty values
data.sort(key=lambda d: float(d['download_speed_ms']) if d.get('download_speed_ms') else 0, reverse=True)

# Display sorted results
for d in data:
    print(f"SSID: {d['ssid']}")
    print('==================')
    print(f"Provider: {d['provider']}")
    print(f"Best Server: {d['best_server']}")
    print(f"Distance: {d['distance_km']} km")
    print(f"Ping: {d['ping_ms']} ms")
    print(f"Download Speed: {d['download_speed_ms']} Mbps")
    print(f"Upload Speed: {d['upload_speed_ms']} Mbps")
    print()

if USE_GRAPHIC:
    # Prepare the data for plotting
    ssids = [d['ssid'] for d in data]
    download_speeds = [float(d['download_speed_ms']) if d['download_speed_ms'] else 0 for d in data]
    upload_speeds = [float(d['upload_speed_ms']) if d['upload_speed_ms'] else 0 for d in data]
    pings = [float(d['ping_ms']) if d['ping_ms'] else 0 for d in data]

    # Create a single figure with 2 rows and 2 columns of subplots
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))

    def plot_subplot(ax, y_data, title, ylabel, colors):
        """Plot individual subplots with each bar getting a unique color."""
        bars = ax.bar(ssids, y_data)  # Create bars first

        # Assign colors to each bar
        for idx, bar in enumerate(bars):
            bar.set_color(colors[idx % len(colors)])  # Use modulo to cycle through colors

        ax.set_xlabel('SSID')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(range(len(ssids)))  # Set tick positions for each bar
        ax.set_xticklabels(ssids, rotation=25, ha='right')

    # Plot each metric in a separate subplot with different colors
    plot_subplot(axes[0, 0], download_speeds, 'Download Speed (Mbps)', 'Download Speed (Mbps)', BAR_COLORS)  # Top-left
    plot_subplot(axes[0, 1], upload_speeds, 'Upload Speed (Mbps)', 'Upload Speed (Mbps)', BAR_COLORS)  # Top-right

    # Only one plot for the second row (bottom plot), merging two columns
    plot_subplot(axes[1, 0], pings, 'Ping (ms)', 'Ping (ms)', BAR_COLORS)  # Bottom-left
    fig.delaxes(axes[1, 1])  # Remove the empty plot on the bottom-right

    # Adjust layout to avoid overlap and save the figure
    plt.tight_layout()

    # Display the figure with all subplots
    plt.show()

