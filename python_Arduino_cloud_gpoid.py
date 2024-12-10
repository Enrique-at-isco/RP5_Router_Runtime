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


# Threshold for deciding when the light is on or off
THRESHOLD = 500  # Adjust based on sensor readings, this is an example

# File to store the log data
CSV_FILE = 'signal_log_test.csv'

csvfile = 'temp.csv'

def logging_func():

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )   


# Function to simulate reading the photoresistor signal (replace with actual sensor code)
def read_signal():
    # Simulating a fluctuating signal, for testing only
    return random.randint(0, 1023)  # Range for 10-bit ADC

# Function to log the blinking or off signal durations
def log_signal_duration(blinking_duration, off_duration):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([blinking_duration, off_duration, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())])




# Function to monitor and log the signal's blinking and off times
def monitor_signal():
    is_blinking = False
    start_time = time.time()
    while True:
        signal = read_signal()  # Read the current signal from the photoresistor
        
        if signal > THRESHOLD:  # Light is on (blinking)
            if not is_blinking:
                # If previously off, record the off period duration
                off_duration = time.time() - start_time
                log_signal_duration(0, off_duration)
                start_time = time.time()  # Reset the timer
            is_blinking = True
        else:  # Light is off (no blinking)
            if is_blinking:
                # If previously on, record the blinking period duration
                blinking_duration = time.time() - start_time
                log_signal_duration(blinking_duration, 0)
                start_time = time.time()  # Reset the timer
            is_blinking = False

        # Sleep for a short time to simulate continuous monitoring (adjust as needed)
        time.sleep(0.1)



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

        client.update()
        #return pin_number
        line.release()
        
        timeC = time.strftime("%I")+':' +time.strftime("%M")+':'+time.strftime("%S")
        data = [value, timeC]
        with open(csvfile, "a")as output:
            writer = csv.writer(output, delimiter=",", lineterminator = '\n')
            writer.writerow(data)
        time.sleep(6) # update script every 60 seconds


if __name__ == "__main__":

    logging_func()
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY,sync_mode=True)

    client.register("Photoresistor_17")
    client.register("is_on")
    client.start()
    read_pin_17()
        
