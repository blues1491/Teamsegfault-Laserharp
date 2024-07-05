import RPi.GPIO as GPIO
import time

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set up the GPIO pin
photo_pin = 17
GPIO.setup(photo_pin, GPIO.IN)

try:
    while True:
        if GPIO.input(photo_pin) == GPIO.LOW:
            print("Light Detected")
        else:
            print("No Light Detected")
        time.sleep(0.5)
finally:
    GPIO.cleanup()
