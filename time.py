def seconds_to_hms(seconds):
    # Calculate hours, minutes, and seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    # Format the result as a string in hr:min:sec
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Example usage
time_string = seconds_to_hms(16208)
print(time_string)  # Output: "04:30:08"
