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
from machine_state import 

# Threshold for deciding when the light is on or off
THRESHOLD = 500  # Adjust based on sensor readings, this is an example

# File to store the log data
#CSV_FILE = 'signal_log_test.csv'

#csvfile = 'temp.csv'

def logging_func():

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )   



# Function to log the blinking or off signal durations
#def log_signal_duration(blinking_duration, off_duration):
 #   with open(CSV_FILE, mode='a', newline='') as file:
 #       writer = csv.writer(file)
#      writer.writerow([blinking_duration, off_duration, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())])


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


def monitor_signal():
    is_blinking = read_pin_17()
    start_time = time.time()
    while True:
        #for i in range(500):
        signal = read_pin_17()  # Read the current signal from the photoresistor
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


#this function reads data from pin 17 and then saves it to csv with timestamp
def read_pin_17():
     
    pin_number = 4
  
    while True:
        chip=gpiod.Chip('gpiochip0')
        line = chip.get_line(pin_number)
        line.request(consumer='my-app',type=gpiod.LINE_REQ_DIR_IN)
        value= line.get_value()
        print(f"Value of gpio{pin_number}: {value}")
        client["Photoresistor_17"] = value
        client["is_on"]= bool(value)
        client["is_off"] = not bool(value)
        client.update()
        #return pin_number
        line.release()
        return value



if __name__ == "__main__":

    logging_func()
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY,sync_mode=True)

    client.register("Photoresistor_17")
    client.register("is_on")
    client.register("is_off")
    client.start()
    read_pin_17()
        
