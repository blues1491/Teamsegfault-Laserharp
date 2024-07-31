import pygame
import pigpio
import threading
import time


# Installation:
#   sudo apt-get install python3-pygame pigpio
#   pip3 install pigpio
# Setup:
#    sudo systemctl enable pigpiod
#    sudo systemctl start pigpiod
# Run: sudo python3 Main.py


# Initialize pygame mixer
pygame.mixer.init()

# Define the monitorGPIO function
def monitorGPIO(gpio_pin, sound_file, folder):
    pi = pigpio.pi()
    if not pi.connected:
        print(f"Failed to connect to pigpio daemon for pin {gpio_pin}")
        return

    pi.set_mode(gpio_pin, pigpio.INPUT)

    sound = pygame.mixer.Sound(folder + sound_file)

    while True:
        value = pi.read(gpio_pin)
        if value == 0:  # Reading input from laser
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

    pi = pigpio.pi()
    if not pi.connected:
        print("GPIO initialization failed.")
        return

    threads = []

    for gpio_pin, sound_file in gpio_to_sound.items():
        t = threading.Thread(target=monitorGPIO, args=(gpio_pin, sound_file, folder))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    pi.stop()

if __name__ == "__main__":
    main()
