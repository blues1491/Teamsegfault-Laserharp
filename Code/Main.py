import pygame
import RPi.GPIO as GPIO
import threading
import tkinter as tk
from tkinter import ttk
import os

# Initialize pygame mixer
pygame.mixer.init()

# Global variables for settings
base_folder = "Sound Samples/"
current_folder = base_folder + "Harp/"
volume = 1.0
current_octave = 3  # Default octave
sound_objects = {}  # Dictionary to store sound objects
threads = []
running = False  # Flag to check if the harp is running
octave_range = [2, 3, 4, 5, 6]  # Supported octaves

gpio_to_note = {
    21: "C",
    20: "C#",
    16: "D",
    12: "D#",
    25: "E",
    24: "F",
    23: "F#",
    18: "G",
    15: "G#",
    14: "A",
    13: "A#",
    19: "B",
    26: "C"
}

def preload_sounds():
    """Preload all sound files to ensure they are ready for playback."""
    global sound_objects
    sound_objects = {}
    for gpio_pin, note in gpio_to_note.items():
        if gpio_pin == 26:
            sound_file = f"{note}{current_octave + 1}.wav"
        else:
            sound_file = f"{note}{current_octave}.wav"
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

    for gpio_pin in gpio_to_note.keys():
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

def choose_folder(folder_name):
    global current_folder
    current_folder = base_folder + folder_name + "/"
    if running:
        preload_sounds()  # Reload sounds with the new folder

def change_octave(value):
    global current_octave
    current_octave = int(value)
    if running:
        preload_sounds()  # Reload sounds with the new octave

def open_main_menu():
    global start_button
    global root
    root = tk.Tk()
    root.title("Laser Harp Main Menu")

    ttk.Label(root, text="Laser Harp", font=("Helvetica", 16)).pack(pady=20)

    start_button = ttk.Button(root, text="Start", command=start_harp)
    start_button.pack(pady=10)

    ttk.Label(root, text="Adjust Volume").pack(pady=10)
    volume_slider = ttk.Scale(root, from_=0, to=1, orient='horizontal', command=adjust_volume)
    volume_slider.set(volume)
    volume_slider.pack(pady=10)

    ttk.Label(root, text="Select Octave").pack(pady=10)
    octave_dropdown = ttk.Combobox(root, values=octave_range)
    octave_dropdown.set(current_octave)
    octave_dropdown.bind("<<ComboboxSelected>>", lambda e: change_octave(octave_dropdown.get()))
    octave_dropdown.pack(pady=10)

    # Get all folders in the Sound Samples directory
    instrument_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

    ttk.Label(root, text="Select Instrument").pack(pady=10)
    instrument_dropdown = ttk.Combobox(root, values=instrument_folders)
    instrument_dropdown.set(os.path.basename(current_folder.strip("/")))
    instrument_dropdown.bind("<<ComboboxSelected>>", lambda e: choose_folder(instrument_dropdown.get()))
    instrument_dropdown.pack(pady=10)

    ttk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    open_main_menu()
