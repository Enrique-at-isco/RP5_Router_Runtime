import time
import math
import datetime
# while True:
#    time.sleep(1)
#     current_time = time.time()
#     formatted_current_time =datetime.datetime.fromtimestamp(current_time)
#     #formatted_current_time = time.strftime('%H:%M:%S',current_time)
#     print(current_time)
#     print(type(current_time))
#     print(formatted_current_time)
#     print(type(formatted_current_time))

import csv

def calculate_state_durations(csv_filename):
    # Initialize the durations for each state
    state_durations = {0: 0, 1: 0, 2: 0}
    
    # Read the CSV file
    with open(csv_filename, mode='r') as file:
        reader = csv.reader(file)
        # Skip the header row if there is one
        next(reader)
        
        # Initialize variables for the state and start timestamp
        previous_state = None
        start_timestamp = None
        
        for row in reader:
            state = int(row[0])
            timestamp = float(row[1])
            
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
    
    return state_durations


# Example usage
csv_filename = 'data/2024_12_16.csv'  # Path to your CSV file
durations = calculate_state_durations(csv_filename)
print(durations)



    