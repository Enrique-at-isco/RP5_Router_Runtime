import time
import logging
import time
import sys
import RPi.GPIO as GPIO
sys.path.append("lib")

from arduino_iot_cloud import ArduinoCloudClient

DEVICE_ID =  "0bdff59d-04b9-44a8-89b1-2c1ecc24dbc4"
SECRET_KEY =  "ekcJUSH37kQhdZC049T8uckGc"

def logging_func():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )   

# This function is executed each time the "test_switch" variable changes 
def on_switch_changed(client, value):
    print("Switch Pressed! Status is: ", value)

def read_GPIO():

    # Set up GPIO
    GPIO.setmode(GPIO.BCM)  # Use BCM numbering
    GPIO.setwarnings(False)

    # Define pin number
    GPIO_PIN = 18

    # Set up the GPIO pin as an input
    GPIO.setup(GPIO_PIN, GPIO.IN)

    # read and print gpio pin value
    try:
        while True:
            # Read the state of the pin
            pin_value = GPIO.input(pin_number)

            print("Pin {} value: {}".format(pin_number, pin_value))

            time.sleep(1)  # Add a delay
    # Clean up
    except KeyboardInterrupt:
    # Cleanup GPIO on exit
     GPIO.cleanup()



if __name__ == "__main__":

    logging_func()
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)

    client.register("test_value")  
    client["test_value"] = 20
    client.register("test_switch", value=None, on_write=on_switch_changed)
    
    client.start()