#!/usr/bin/env python3

import threading
import requests
import time
import subprocess
from joyit_mfrc522 import MFRC522
import RPi.GPIO as GPIO
import ITS_options as config
# Initialize the RFID reader
reader = MFRC522()

# RSU ID (replace with actual ID)
RSU_ID = config.RSU_ID

# Web App URLs
LOCKED_DEVICES_URL = config.LOCKED_DEVICES_URL  # URL to fetch locked devices "http://127.0.0.1:5000/api/locked-devices"

REPORT_THEFT_URL = config.REPORT_THEFT_URL # URL to report theft "http://127.0.0.1:5000/api/report-theft"      

# Function to fetch locked RFIDs from the database
def fetch_locked_devices():
    try:
        # TODO Add additional request handling to fetch all devices, not just locked ones
        response = requests.get(LOCKED_DEVICES_URL)
        if response.status_code == 200:
            locked_devices = response.json().get("locked_bike_ids", [])
            print(f"Locked devices fetched: {locked_devices}")
            return locked_devices
        else:
            print(f"Error fetching locked devices: {response.status_code}")
    except Exception as e:
        print(f"Exception during fetch: {e}")
    return []

# Function to send a theft report
def report_theft(rfid):
    try:
        # Prepare theft report payload and send it to the server
        payload = {
            "rfid": rfid,
            "rsu_id": RSU_ID,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        response = requests.post(REPORT_THEFT_URL, json=payload)
        if response.status_code == 200:
            print(f"Theft report sent successfully for RFID: {rfid}")
        else:
            print(f"Error sending theft report: {response.status_code}")
    except Exception as e:
        print(f"Exception during report: {e}")

# Function to scan RFID tags
def scan_rfid():
    print("Starting RFID scanning...")
    watchlist = set()  # Tracks locked RFIDs in the detection zone
    persistent_scan = set()  # Tracks consistently detected RFIDs
    debounce_count = {}  # Tracks detection stability using a debounce mechanism
    debounce_threshold = 2  # Number of consecutive detections to stabilize

    # Mapping RFID tags to IDs (example mapping for known tags)
    tag_mapping = {
        "d9:5d:42:83": 2936,
        "ed:fe:24:03": 7964,
        "18:01:f8:bb": 8136,
    }

    try:
        while True:
            current_scan = set()  # Tracks RFIDs detected in the current scan

            # Detect a tag
            (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
            if status == reader.MI_OK:
                print("Tag detected")

            # Get the card's UID
            (status, uid) = reader.MFRC522_Anticoll()
            if status == reader.MI_OK:
                uid_first4 = uid[:4]  # Use the first 4 bytes of the UID
                uid_hex = ":".join(f"{byte:02x}" for byte in uid_first4)
                print(f"Card UID (First 4 Bytes, Hex): {uid_hex}")

                # Map the UID to the desired ID
                mapped_id = tag_mapping.get(uid_hex)
                if mapped_id:
                    print(f"Mapped UID {uid_hex} to ID {mapped_id}")
                    current_scan.add(mapped_id)
                else:
                    # TODO Handle unknown RFIDs (not mapped) appropriately
                    print(f"UID {uid_hex} is not mapped to any ID")

            # Debounce logic to stabilize detection
            for rfid in current_scan:
                if rfid in debounce_count:
                    debounce_count[rfid] += 1
                else:
                    debounce_count[rfid] = 1

                if debounce_count[rfid] >= debounce_threshold:
                    persistent_scan.add(rfid)

            # Remove RFIDs no longer detected
            for rfid in list(persistent_scan):
                if rfid not in current_scan:
                    debounce_count[rfid] -= 1
                    if debounce_count[rfid] <= 0:
                        persistent_scan.remove(rfid)
                        debounce_count.pop(rfid, None)

            # Fetch locked devices from the Web App
            locked_devices = fetch_locked_devices()

            # Process detected RFIDs
            for rfid in persistent_scan:
                if rfid in locked_devices:
                    if rfid in watchlist:
                        print(f"RFID {rfid} is already on the watchlist.")
                    else:
                        # TODO Modify the following, script can't automatically add to watchlist
                        print(f"RFID {rfid} is locked but not on the watchlist. Adding to watchlist...")
                        watchlist.add(rfid)  # Add to the watchlist
                else:
                    # TODO Implement handling for unlocked RFIDs
                    print(f"RFID {rfid} is detected but is not locked.")

            # Check for RFIDs that move out of the detection zone
            for rfid in list(watchlist):
                if rfid not in persistent_scan:
                    # TODO Ensure theft reporting follows logic to avoid false positives
                    print(f"RFID {rfid} moved out of detection zone. Reporting theft...")
                    report_theft(rfid)
                    watchlist.remove(rfid)

            # Display current status
            print("\nCurrent Status:")
            print(f"Watchlist: {list(watchlist)}")
            print(f"Detected Tags: {list(persistent_scan)}")

            time.sleep(4)
    except KeyboardInterrupt:
        print("Stopping RFID scanning...")
    finally:
        GPIO.cleanup()  # Cleanup GPIO pins on exit
        print("GPIO cleaned up. Exiting...")

# Run RFID scanning in a background thread
# def start_rfid_scanning():
#     # Start the RFID scanning in a separate thread to avoid blocking
#     thread = threading.Thread(target=scan_rfid, daemon=True)
#     thread.start()

# # Main entry point
# if __name__ == "__main__":
#     # TODO Implement periodic GET request for parking/leaving messages
#     start_rfid_scanning()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Exiting program...")