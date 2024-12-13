import time
import logging
import time
import sys
import gpiod
import csv
import random
import os
from datetime import datetime
sys.path.append("lib")

from arduino_iot_cloud import ArduinoCloudClient
from secret import DEVICE_ID, SECRET_KEY
import machine_stats

# Threshold for deciding when the light is on or off
THRESHOLD = 500  # Adjust based on sensor readings, this is an example


def logging_func():

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )   


def monitor_signal(sampling_interval=0.1, blink_threshold_on=0.8, blink_threshold_off=0.2):
    """
    Function to detect the LED state based on pin readings, and track the duration in the current state.
    
    Parameters:
    - pin_reading_function: a function that returns the LED pin state (0 or 1).
    - sampling_interval: how frequently to sample the LED pin state (default is 0.1s).
    - blink_threshold_on: threshold for "on" state (default is 0.8).
    - blink_threshold_off: threshold for "off" state (default is 0.2).
    
    Returns:
    - A string indicating the LED state: "Blinking", "On", "Off".
    - The duration the LED has been in that state.
    """
    
    # To track the states and timings
    start_time = time.time()
    on_count = 0
    off_count = 0
    prev_state = None  # Previous state of the LED pin reading
    
    # Variables to track blink timings
    on_duration = 0
    off_duration = 0
    blink_pattern_detected = False
    current_state = None
    state_duration = 0  # Duration of the current state in seconds

    while True:
        current_time = time.time()
        pin_value = read_pin()

        # Determine if the LED is on or off based on the pin reading
        if pin_value >= blink_threshold_on:
            # LED is on
            if prev_state == 0:  # LED just turned on
                off_duration = current_time - start_time  # End of off period
            start_time = current_time  # Reset the timer
            on_duration += sampling_interval
            prev_state = 1
            new_state = "On"
        elif pin_value < blink_threshold_off:
            # LED is off
            if prev_state == 1:  # LED just turned off
                on_duration = current_time - start_time  # End of on period
            start_time = current_time  # Reset the timer
            off_duration += sampling_interval
            prev_state = 0
            new_state = "Off"
        else:
            new_state = "Unknown"

        # Update the current state and its duration
        if new_state != current_state:
            current_state = new_state
            state_duration = 0  # Reset the state duration when the state changes

        # Increment the state duration as time passes
        state_duration += sampling_interval

        # Check for blinking pattern (on for ~0.8s, off for ~0.2s)
        if on_duration >= blink_threshold_on - 0.1 and on_duration <= blink_threshold_on + 0.1:
            if off_duration >= blink_threshold_off - 0.1 and off_duration <= blink_threshold_off + 0.1:
                blink_pattern_detected = True

        # If blinking pattern is detected, classify the LED as blinking
        if blink_pattern_detected:
            write_to_csv(1,current_time,state_duration)
            client["is_Running"]= True    
            return f"Blinking (Duration: {state_duration:.2f} seconds)"

        # If the LED is on for more than the threshold, classify it as "On"
        if on_duration >= blink_threshold_on:
            write_to_csv(2,current_time,state_duration)
            client["is_Running"]= True    
            return f"On (Duration: {state_duration:.2f} seconds)"

        # If the LED is off for more than the threshold, classify it as "Off"
        if off_duration >= blink_threshold_off:
            write_to_csv(0,current_time,state_duration)
            client["is_Running"]= True    
            return f"Off (Duration: {state_duration:.2f} seconds)"
        client.update()

def read_pin():
     
    pin_number = 4
    chip=gpiod.Chip('gpiochip0')
    line = chip.get_line(pin_number)
    line.request(consumer='my-app',type=gpiod.LINE_REQ_DIR_IN)
    value= line.get_value()
    print(f"Value of gpio{pin_number}: {value}")
    client["Photoresistor_17"] = value
    client["is_off"] = not bool(value)
    calculate_total_times('data')
    client.update()
    #return pin_number
    return value
    line.release()


# Function checks and creates .csv with todays date and writes to it
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



# this function calculates the total runtime and downtime during a day and sends that data to ardiuno cloud       
def calculate_total_times(folder_path):
    # Get today's date in YYYY-MM-DD format
    today_date = datetime.today().strftime('%Y_%m_%d')
    
    # Create the CSV file path (combine folder path and today's date as the filename)
    csv_file_path = os.path.join(folder_path, f'{today_date}.csv')
    
    # Check if the file exists
    if not os.path.exists(csv_file_path):
        print(f"No file found for {today_date}.")
        return
    
    # Initialize variables for total on and off times
    total_on_time = 0.0
    total_hold_time = 0.0
    total_off_time = 0.0
    precent_runtime = 0.0
    precent_holdtime = 0.0
    precent_downtime = 0.0
    
    # Open the CSV file and read the data
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        
        # Skip the header row
        next(reader)
        
        # Iterate through each row and sum the times based on the state
        for row in reader:
            state = int(row[0])  # State (0 or 1)
            duration = float(row[2])  # Duration in seconds
            
            if state == 1:
                total_on_time += duration
                total_on_time_formatted = total_on_time/(60)
            elif state ==2:
                total_hold_time +=duration
                total_hold_time_formatted = total_off_time/(60)
            elif state == 0:
                total_off_time += duration
                total_off_time_formatted = total_off_time/(60)
    
    precent_runtime = (total_on_time/(total_on_time+total_off_time+total_hold_time))*100
    precent_holdtime = (total_hold_time/(total_on_time+total_off_time+total_hold_time))*100
    precent_downtime = (total_off_time/(total_on_time+total_off_time+total_hold_time))*100
    # Print the results
    print(f"Total On Time for {today_date}: {total_on_time:.2f} seconds")
    print(f"Total Off Time for {today_date}: {total_off_time:.2f} seconds")
    print(f"Total Off Time for {today_date}: {total_hold_time:.2f} seconds")
    client["todays_Runtime"] = total_on_time_formatted
    client["todays_Downtime"] = total_off_time_formatted
    client["todays_Holding_Time"] = total_hold_time_formatted
    client["precent_Downtime"] = precent_downtime
    client["precent_Runtime"] = precent_runtime
    client["precent_Holdtime"] = precent_holdtime


if __name__ == "__main__":

    logging_func()
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY,sync_mode=True)

    client.register("Photoresistor_17")
    client.register("is_Running")
    client.register("todays_Runtime")
    client.register("todays_Downtime")
    client.register("todays_Holding_Time")
    client.register("precent_Runtime")
    client.register("precent_Downtime")

    client.start()
    monitor_signal()

        
