import gpiod
import time

# Define GPIO pin
LED_PIN = 4

# Access the GPIO chip and pin
chip = gpiod.Chip("gpiochip0")
line = chip.get_line(LED_PIN)

# Configure the pin as an input
line.request(consumer="my_program", type=gpiod.LINE_REQUEST_DIRECTION_IN)

# Read the pin's value
value = line.get_value()
print(f"GPIO pin {LED_PIN} value: {value}")

# Release the line
line.release()