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
#import machine_stats

# Threshold for deciding when the light is on or off
THRESHOLD = 500  # Adjust based on sensor readings, this is an example


def logging_func():

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )   


def monitor_signal(sampling_interval=0.1,blink_threshold_on=0.8, blink_threshold_off=0.2):
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
    #start_time = time.strftime('%H:%M:%S', time.localtime(start_time))
    
    on_count = 0
    off_count = 0
    prev_state = None  # Previous state of the LED pin reading
    
    # Variables to track blink timings
    on_duration = 0
    off_duration = 0
    blink_pattern_detected = False
    current_state = None
    state_duration = 0  # Duration of the current state in seconds
    state = 1
    while True:
        current_time = time.time()
        #check if time is still within the work shift
        now = datetime.now()
        current_time = now.time()
        if current_time.hour > 17 or (current_time.hour == 17 and current_time.minute > 30):
            print("Task stopped as time is out of the interval.")
            break
        #read the pin
        pin_value = read_pin()
        #current_time= time.strftime('%H:%M:%S', time.localtime(start_time))
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
            change = 1
            #write_to_csv(current_state,current_time, state_duration)
            current_state = new_state
            state_duration = 0  # Reset the state duration when the state changes
        else: change =0
        #write_to_csv(change,current_state,current_time, state_duration)
        # Increment the state duration as time passes
        state_duration += sampling_interval
        #print(state_duration)
        # Check for blinking pattern (on for ~0.8s, off for ~0.2s)
        if on_duration >= blink_threshold_on - 0.1 and on_duration <= blink_threshold_on + 0.1:
            if off_duration >= blink_threshold_off - 0.1 and off_duration <= blink_threshold_off + 0.1:
                blink_pattern_detected = True
        
        # If blinking pattern is detected, classify the LED as blinking
        if blink_pattern_detected:
            #write_to_csv(change, 1,current_time,state_duration)
            state = 1
            client["is_Running"]= True  
            blink_pattern_detected = False  
            #return f"Blinking (Duration: {state_duration:.2f} seconds)"

        # If the LED is on for more than the threshold, classify it as "On"
        elif on_duration >= blink_threshold_on:
            #write_to_csv(change,2,current_time,state_duration)
            state = 2
            client["is_Running"]= True    
            #return f"On (Duration: {state_duration:.2f} seconds)"

        # If the LED is off for more than the threshold, classify it as "Off"
        elif off_duration >= blink_threshold_off:
            state = 0
            #write_to_csv(change, 0,current_time,state_duration)
            client["is_Running"]= False
            #return f"Off (Duration: {state_duration:.2f} seconds)"
            
        write_to_csv(change,state,current_time,state_duration)
        
        calculate_total_times('data')
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
   
    #client.update()
    #return pin_number
    return value
    line.release()


# Function checks and creates .csv with todays date and writes to it
def write_to_csv(state_change ,state, start_time, duration):
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
            writer.writerow([state, start_time, duration])
        if state_change == 1:
            # Write the data to the file (data is a list: [State, Start Time, Duration])
            writer.writerow([state, start_time, duration])
    if state_change == 0:
        update_last_line(csv_file_path, [state, start_time, duration])
        
#Function updates the last line in a .csv file
def update_last_line(csv_file,new_values):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        #print(rows)
    rows[-1] = new_values
    
    with open(csv_file,'w', newline='') as file:
        writer= csv.writer(file)
        writer.writerows(rows)


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
    total_on_time_formatted = 0.0
    total_hold_time_formatted = 0.0
    total_off_time_formatted = 0.0
    precent_runtime = 0.0
    precent_holdtime = 0.0
    precent_downtime = 0.0
    
    state_durations = {0: 0, 1: 0, 2: 0}        
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        #print(reader)
        # Skip the header row if there is one
        next(reader)
        
        # Initialize variables for the state and start timestamp
        previous_state = None
        start_timestamp = None
        
        for row in reader:
            state = int(row[0])
            timestamp = float(row[1])
            #print(state)
            # If we are switching states, accumulate the duration of the previous state
            if previous_state is not None and previous_state != state:
                state_durations[previous_state] += timestamp - start_timestamp
            
            # If the state is the same as the previous one, we just accumulate the time
            if previous_state == state:
                state_durations[state] += timestamp - start_timestamp

            # Update the start timestamp for the new state
            start_timestamp = timestamp
            
            # Update the previous state to the current one
            previous_state = state
        
        # After finishing the loop, handle the last state duration
        if previous_state is not None:
            state_durations[previous_state] += timestamp - start_timestamp


        total_on_time = state_durations[0]
        total_off_time = state_durations[2]
        total_hold_time = state_durations[1]
        total_time = total_on_time + total_off_time + total_hold_time
        if total_time > 0:
            precent_runtime = (total_on_time/(total_on_time+total_off_time+total_hold_time))*100
            precent_holdtime = (total_hold_time/(total_on_time+total_off_time+total_hold_time))*100
            precent_downtime = (total_off_time/(total_on_time+total_off_time+total_hold_time))*100
# Print the results
    runtime= seconds_to_hms(total_on_time)
    downtime = seconds_to_hms(total_off_time)
    holdtime = seconds_to_hms(total_hold_time)
    print(f"Total On Time for {today_date}: {total_on_time}")
    print(f"Total Off Time for {today_date}: {total_off_time}")
    print(f"Total hold Time for {today_date}: {total_hold_time}")
    client["todays_Runtime_sec"] = str(runtime['sec'])
    client["todays_Runtime_min"] = str(runtime['min'])  
    client["todays_Runtime_hr"] = str(runtime['hr'])
    #downtime counter
    client["todays_Downtime_sec"] = downtime['sec']
    client["todays_Downtime_min"] = downtime['min']
    client["todays_Downtime_hr"] = downtime['hr']
    #holdtime counter
    client["todays_Holding_Time_sec"] = holdtime['sec']
    client["todays_Holding_Time_min"] = holdtime['min']   
    client["todays_Holding_Time_hr"] = holdtime['hr']  
    clk = str(datetime.fromtimestamp(total_on_time))
    client["clk"] = clk
    #print(clk)
    client["precent_Downtime"] = precent_downtime
    client["precent_Runtime"] = precent_runtime
    client["precent_Holdtime"] = precent_holdtime

def is_within_time_interval(start_hour=7, start_minute=0, end_hour=17, end_minute=30):
    """
    Check if the current time is between the specified interval (default: 7:00 AM to 5:30 PM)
    and only on weekdays (Monday to Friday).
    """
    while True:
        now = datetime.now()
        current_time = now.time()
        current_weekday = now.weekday()  # Monday is 0 and Sunday is 6
        print(current_time)
        print(current_weekday)
        # Define start and end time for the interval
        start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0).time()
        end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0).time()

        # Check if the current time is within the interval and today is a weekday
        if start_time <= current_time <= end_time and current_weekday < 5:
            monitor_signal()

        # Sleep for a while before checking again
        time.sleep(60)  # Check every minute
    
def seconds_to_hms(seconds):
    time_formatted = {'hr': 0, 'min': 0, 'sec': 0}       
    # Calculate hours, minutes, and seconds
    time_formatted['hr'] = int(seconds // 3600)
    time_formatted['min'] = int((seconds % 3600) // 60)
    time_formatted['sec'] = int(seconds % 60)
    
    # Format the result as a string in hr:min:sec
    return time_formatted
    
if __name__ == "__main__":

    logging_func()
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY,sync_mode=True)

    client.register("Photoresistor_17")
    client.register("is_Running")
    client.register("is_off")
    client.register("todays_Runtime_sec")
    client.register("todays_Runtime_min")
    client.register("todays_Runtime_hr")
    
    client.register("todays_Downtime_sec")
    client.register("todays_Downtime_min")
    client.register("todays_Downtime_hr")
    
    client.register("todays_Holding_Time_sec")
    client.register("todays_Holding_Time_min")    
    client.register("todays_Holding_Time_hr")
    client.register("precent_Runtime")
    client.register("precent_Downtime")
    client.register("precent_Holdtime")
    #client.register("clk",value=None, on_read=lambda x: time.strftime("%H:%M:%S",time.localtime()), interval =0.1)
    client.register("clk")
    client.start()
    is_within_time_interval()
    

        
