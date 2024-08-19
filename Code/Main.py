import pygame
import RPi.GPIO as GPIO
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Initialize pygame mixer
pygame.mixer.init()

# Global variables for settings
current_folder = "Sound Samples/Piano/"
volume = 1.0
sound_objects = {}  # Dictionary to store sound objects
threads = []
running = False  # Flag to check if the harp is running
gpio_to_sound = {
    21: "C3.wav",
    20: "D3.wav",
    16: "E3.wav",
    12: "F3.wav",
    25: "G3.wav",
    24: "A3.wav",
    23: "B3.wav"
}

def preload_sounds():
    """Preload all sound files to ensure they are ready for playback."""
    global sound_objects
    sound_objects = {}
    for gpio_pin, sound_file in gpio_to_sound.items():
        sound = pygame.mixer.Sound(current_folder + sound_file)
        sound.set_volume(volume)
        sound_objects[gpio_pin] = sound

def monitorGPIO(gpio_pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    sound = sound_objects[gpio_pin]

    while running:
        value = GPIO.input(gpio_pin)
        if value == GPIO.HIGH:
            sound.play()

def start_harp():
    global running, threads
    running = True
    preload_sounds()
    threads = []

    for gpio_pin in gpio_to_sound.keys():
        thread = threading.Thread(target=monitorGPIO, args=(gpio_pin,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_button.config(text="Stop", command=stop_harp)

def stop_harp():
    global running
    running = False
    for thread in threads:
        thread.join()  # Wait for all threads to finish
    
    GPIO.cleanup()
    start_button.config(text="Start", command=start_harp)

def adjust_volume(value):
    global volume
    volume = float(value)
    for sound in sound_objects.values():
        sound.set_volume(volume)

def choose_folder():
    global current_folder
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected + "/"
        if running:
            stop_harp()
            start_harp()

def open_main_menu():
    global start_button
    main_menu = tk.Tk()
    main_menu.title("Laser Harp Main Menu")

    ttk.Label(main_menu, text="Laser Harp", font=("Helvetica", 16)).pack(pady=20)

    start_button = ttk.Button(main_menu, text="Start", command=start_harp)
    start_button.pack(pady=10)

    ttk.Button(main_menu, text="Settings", command=open_settings).pack(pady=10)
    ttk.Button(main_menu, text="Exit", command=main_menu.quit).pack(pady=10)

    main_menu.mainloop()

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Settings")

    ttk.Label(settings_window, text="Adjust Volume").pack(pady=10)
    volume_slider = ttk.Scale(settings_window, from_=0, to=1, orient='horizontal', command=adjust_volume)
    volume_slider.set(volume)
    volume_slider.pack(pady=10)

    ttk.Button(settings_window, text="Change Instrument Folder", command=choose_folder).pack(pady=10)

    settings_window.mainloop()

if __name__ == "__main__":
    open_main_menu()
