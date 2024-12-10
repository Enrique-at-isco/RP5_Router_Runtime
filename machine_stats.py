import os
import csv
from datetime import datetime

def calculate_total_times(folder_path):
    # Get today's date in YYYY-MM-DD format
    today_date = datetime.today().strftime('%Y-%m-%d')
    
    # Create the CSV file path (combine folder path and today's date as the filename)
    csv_file_path = os.path.join(folder_path, f'{today_date}.csv')
    
    # Check if the file exists
    if not os.path.exists(csv_file_path):
        print(f"No file found for {today_date}.")
        return
    
    # Initialize variables for total on and off times
    total_on_time = 0.0
    total_off_time = 0.0
    
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
            elif state == 0:
                total_off_time += duration
    
    # Print the results
    print(f"Total On Time for {today_date}: {total_on_time:.2f} seconds")
    print(f"Total Off Time for {today_date}: {total_off_time:.2f} seconds")

    total_times= [total_on_time,total_off_time]    
    return total_times

# Example usage
folder = '/path/to/your/folder'  # Replace with the correct folder path
calculate_total_times(folder)
