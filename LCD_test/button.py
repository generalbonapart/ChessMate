import RPi.GPIO as GPIO
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number where the button is connected
BUTTON_PIN = 4

# Set up the button pin as an input with a pull-up resistor
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Read the button status
        button_state = GPIO.input(BUTTON_PIN)
        
        if button_state == GPIO.LOW:
            print("Button pressed")
        else:
            print("Button released")
        
        # Wait for a short period of time to debounce the button
        time.sleep(0.1)

except KeyboardInterrupt:
    # Clean up GPIO settings before exiting
    GPIO.cleanup()
