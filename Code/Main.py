import pygame
import RPi.GPIO as GPIO
import threading
import time


# Install dependencies: 
#   sudo apt-get install python3-pygame python3-rpi.gpio
# Run with: 
#   sudo python3 laser_harp.py


# Initialize pygame mixer
pygame.mixer.init()

# Define the monitorGPIO function
def monitorGPIO(gpio_pin, sound_file, folder):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    sound = pygame.mixer.Sound(folder + sound_file)

    while True:
        value = GPIO.input(gpio_pin)
        if value == GPIO.LOW:  # Reading input from laser
            sound.play()
            while pygame.mixer.get_busy():
                time.sleep(0.01)

# Main function
def main():
    folder = "Sound Samples/"
    gpio_to_sound = {
        21: "C3.wav",
        20: "D3.wav",
        16: "E3.wav",
        12: "F3.wav",
        25: "G3.wav",
        24: "A3.wav",
        23: "B3.wav"
    }

    threads = []

    for gpio_pin, sound_file in gpio_to_sound.items():
        t = threading.Thread(target=monitorGPIO, args=(gpio_pin, sound_file, folder))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    GPIO.cleanup()

if __name__ == "__main__":
    main()


# To convert to exe
#   Install PyInstaller:
#       pip install pyinstaller
#   Run:
#       pyinstaller --onefile --noconsole laser_harp.py 
