# Wifi Speed Test Automation

## Overview

This project automates the process of running speed tests across multiple WiFi profiles, collecting the results, and visualizing the data. It connects to each WiFi network in a list of profiles, performs a speed test, and stores the results in a file. The results can then be analyzed with graphs that display download speed, upload speed, and ping for each WiFi network.

## Features

- **Automated WiFi profile switching**: The script automatically connects to multiple WiFi networks in sequence, based on profiles stored in a JSON file.
- **Speed testing**: Uses the `speedtest-cli` tool to run speed tests for each WiFi network and store the results.
- **Data visualization**: Displays the results of speed tests in a bar chart format, showing download speed, upload speed, and ping for each network.

## Requirements

- **Python 3.x**
- **Libraries**:
  - `pywifi` (for managing WiFi connections)
  - `speedtest-cli` (for running speed tests)
  - `matplotlib` (for plotting graphs)
  - `argparse` (for command-line arguments)
  - `json` (for reading WiFi profiles)

## Installation

1. **Clone the repository**:
   
   ```
   git clone https://github.com/ac-jurd/wifi-multitest.git
   cd wifi-multitest
   ```
2. **Install dependencies:**
   
   ```bash
   pip install pywifi speedtest-cli matplotlib
   ```
3. Set up profiles
   - Create a `profiles.json` file containing the WiFi network profiles you want to test. Each profile should include the SSID and password. Example format:
     
     ```json
     [
         {
             "ssid": "Network1",
             "key": "password1"
         },
         {
             "ssid": "Network2",
             "key": "password2"
         }
     ]
     ```

## Usage

### Run WiFi Speed Test

To run the script and perform the speed tests, execute the following command:

```bash
python main.py
```

This will:

1. Connect to each WiFi network in the `profiles.json` file.

2. Perform a speed test using `speedtest-cli`.

3. Save the results in a text file named `speedtest-<SSID>.txt`.

You can optionally specify a server for the speed test using the `--server` flag:

```bash
python main.py --server <server_id>
```

Where `<server_id>` is the ID of the speed test server you want to use.

### Data Analysis

Once the speed tests have completed, you can analyze the results by running the analysis script:

```bash
python analysis.py
```

This will:

1. Read the speed test results from the `speedtest-<SSID>.txt` files.

2. Generate a bar chart showing:
   
   - Download speed (Mbps)
   
   - Upload speed (Mbps)
   
   - Ping (ms)

## Script Explanation

### `main.py`

This script:

- Reads WiFi profiles from the `profiles.json` file.
- Connects to each WiFi profile.
- Runs the speed test using `speedtest-cli`.
- Stores the results in a text file.

### `analyze_results.py`

This script:

- Reads the speed test result files.
- Extracts the data for download speed, upload speed, and ping.
- Sorts the data by download speed.
- Displays the results as bar charts using `matplotlib`.

## Configuration

You can configure the following settings in `main.py`:

- `MAX_ATTEMPTS`: The maximum number of attempts to connect to a WiFi profile before moving to the next one.
- `ATTEMPT_LENGTH`: The amount of time (in seconds) to wait between each connection attempt.
- `WAIT_BETWEEN_TESTS`: The wait time (in seconds) between each WiFi connection and speed test.
- `PROFILE_DATA_FILENAME`: The name of the JSON file containing the WiFi profiles (`profiles.json`).

## Troubleshooting

- **Speedtest-cli not found**: Ensure that the `speedtest-cli` executable is in your PATH. You can install it using:
  
  ```bash
  pip install speedtest-cli
  ```

- **Unable to connect to WiFi**: Ensure that your WiFi interface is up and that the profiles in `profiles.json` are correct.

- **Permission issues**: You might need to run the script with administrator privileges on certain systems to allow network interface management.

## License

This project is licensed under the MIT License.
