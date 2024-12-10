import time
import csv
import random  # Simulate the signal for testing purposes (remove in real application)
import os
from datetime import datetime
# Threshold for deciding when the light is on or off
THRESHOLD = 500  # Adjust based on sensor readings, this is an example

# File to store the log data
CSV_FILE = 'signal_log_test.csv'

# Function to simulate reading the photoresistor signal (replace with actual sensor code)
def read_signal():
    
    # Simulating a fluctuating signal, for testing only
    return random.randint(0, 1)  # Range for 10-bit ADC
    
    
def write_to_csv( state, start_time, duration):
    # Get today's date in YYYY-MM-DD format
    today_date = datetime.today().strftime('%Y_%m_%d')
    
    # Create the CSV file path (combine folder path and today's date as the filename)
    csv_file_path = os.path.join('data', f'{today_date}.csv')
    
    # Check if the file exists to decide if we need to write the header
    file_exists = os.path.exists(csv_file_path)
    
    # Open the CSV file in append mode (no data will be erased)
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # If the file does not exist, write the header first
        if not file_exists:
            writer.writerow(['State', 'Start Time', 'Duration'])  # Write header only if the file is new
        
        # Write the data to the file (data is a list: [State, Start Time, Duration])
        writer.writerow([state, start_time, duration])


# Function to log the signal state, start time, and duration into the CSV
#def log_signal_state(state, start_time, duration):
#    with open(CSV_FILE, mode='a', newline='') as file:
#        writer = csv.writer(file)
#        writer.writerow([state, start_time, duration])

# Function to monitor and log the signal's blinking and off times
def monitor_signal():
    is_blinking = read_signal()
    start_time = time.time()
    while True:
        #for i in range(500):
        signal = read_signal()  # Read the current signal from the photoresistor
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

        if signal > THRESHOLD:  # Light is on (blinking)
            if not is_blinking:
                # If previously off, record the off period duration
                off_duration = time.time() - start_time
                if off_duration > 0:
                    write_to_csv(0, current_time, off_duration)  # Log off state
                start_time = time.time()  # Reset the timer
            is_blinking = True
        else:  # Light is off (no blinking)
            if is_blinking:
                # If previously on, record the blinking period duration
                blinking_duration = time.time() - start_time
                if blinking_duration > 0:
                    write_to_csv(1, current_time, blinking_duration)  # Log blinking state
                start_time = time.time()  # Reset the timer
            is_blinking = False

        # Sleep for a short time to simulate continuous monitoring (adjust as needed)
        time.sleep(1)

# Start monitoring the signal
monitor_signal()
