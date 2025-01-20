import time
from json import loads
from typing import List
import subprocess
import pywifi
from pywifi.iface import Interface

# Constants
PROFILE_DATA_FILENAME = 'profiles.json'
MAX_ATTEMPTS = 10
ATTEMPT_LENGTH = 1 # Seconds
WAIT_BETWEEN_TESTS = 3 # Seconds

wifi = pywifi.PyWiFi()

# Check number of available wifi interfaces
if len(wifi.interfaces()) == 0:
    print('Could not find any wifi interfaces')
    exit(1)

# Select default interface
iface: Interface = wifi.interfaces()[0]
print(f'Selected wifi Interface {iface.name()}')

# Save original profile for restoration when script is done
original_profile = None
if iface.status() == pywifi.const.IFACE_CONNECTED:
    current_ssid = iface.network_profiles()[0].ssid
    profiles = iface.network_profiles()
    for profile in profiles:
        if profile.ssid == current_ssid:
            original_profile = profile
            print(f'Saved original profile {profile.ssid}')
            break

# Read profile settings from file
profile_data = []
try:
    with open(PROFILE_DATA_FILENAME, 'r') as file:
        profile_data = loads(file.read())
    print(f'Read {len(profile_data)} profiles from profiles.json\n')
except FileNotFoundError:
    print(f'Unable to find file {PROFILE_DATA_FILENAME}')
    exit(1)
except ValueError as e:
    print(f'Error reading JSON from file {PROFILE_DATA_FILENAME}: {e}')
    exit(1)

# Handle no profile data error
if len(profile_data) == 0:
    print('Zero profiles read from profiles.json')
    exit(1)

# Validate JSON
for i, data in enumerate(profile_data):
    if 'ssid' not in data or 'key' not in data:
        print(f'Profile data {i} invalid (requires ssid and key)')
        exit(1)

# Create empty list of profile objects
profiles: List[pywifi.Profile] = []

# Iterate over profile settings
for i, profile in enumerate(profile_data):
    # Create profile objects
    new_profile = pywifi.Profile()
    new_profile.ssid = profile['ssid']
    new_profile.auth = pywifi.const.AUTH_ALG_OPEN
    new_profile.akm.append(pywifi.const.AKM_TYPE_WPA2)
    new_profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
    new_profile.key = profile['key']

    print(f'#{i}: Created new profile object with SSID \'{new_profile.ssid}\'')

    # Add to list of profile objects
    profiles.append(new_profile)

try:
    # Iterate over list of profile objects
    for i, profile in enumerate(profiles):
        if i >= 1:
            print(f'Wait {WAIT_BETWEEN_TESTS} seconds so speedtest doesn\'t ban my ip')
            time.sleep(WAIT_BETWEEN_TESTS)

        print('\n', end='')

        # Disconnect from current wifi profile
        iface.disconnect()
        print('Disconnected from previous profile')

        for attempt in range(MAX_ATTEMPTS):
            if iface.status() == pywifi.const.IFACE_DISCONNECTED:
                break
            time.sleep(ATTEMPT_LENGTH)
        else:
            print(f'Timeout while disconnecting profile {profile.ssid}')
            continue

        # Connect to current wifi profile
        iface.add_network_profile(profile)
        iface.connect(profile)
        print(f'Initiated connection using profile {profile.ssid}')

        for attempt in range(MAX_ATTEMPTS):
            if iface.status() == pywifi.const.IFACE_CONNECTED:
                break
            time.sleep(ATTEMPT_LENGTH)
        else:
            print(f'Timeout while connecting profile {profile.ssid}')
            continue

        # Perform speedtest via speedtest-cli
        # Write results from stdout to file
        try:
            # Run speedtest-cli, save output to file
            print(f'Running speed test on profile {profile.ssid}')
            with open(f'speedtest-{profile.ssid}.txt', 'w') as file:
                subprocess.run(['speedtest-cli', '--secure'], stdout=file)
            print('Success')
        except FileNotFoundError:
            print('Unable to find speedtest-cli.exe')
            exit(1)
        except subprocess.CalledProcessError as e:
            print(f'Error while running subproces speedtest-cli on profile {profile.ssid}: {e}')
            continue

        # Clean up profile from system if not original profile
        # if original_profile is not None and profile.ssid != original_profile.ssid:
            # iface.remove_network_profile(profile)

finally:
    # If an original profile was saved at the start of the script
    if original_profile:
        print(f'Restoring original profile {original_profile.ssid}')

        # Disconnect from current profile
        iface.disconnect()

        # Check disconnect status with timeout
        for attempt in range(MAX_ATTEMPTS):
            if iface.status() == pywifi.const.IFACE_DISCONNECTED:
                break
            time.sleep(ATTEMPT_LENGTH)
        else:
            # Did not disconnect in the specified amount of time
            print(f'Error while disconnecting iface to restore original profile')
            exit(1)

        # Add original profile to network profiles
        iface.add_network_profile(original_profile)
        # Connect using original profile
        iface.connect(original_profile)

        # Check connection status using timeout
        for attempt in range(MAX_ATTEMPTS):
            if iface.status() == pywifi.const.IFACE_CONNECTED:
                print('Sucessfully reconnected')
                break
            time.sleep(ATTEMPT_LENGTH)
        else:
            # Did not connect in the specified amount of time
            print(f'Error while reconnecting iface to restore original profile')
            exit(1)
    else:
        print('No original profile to restore')

    print('Done')

# Parse results from file, store in dict

# Analyse results dict, connect to fastest AP
