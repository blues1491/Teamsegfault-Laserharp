import pygame
import tkinter as tk
from tkinter import ttk
import os

pygame.mixer.init()

base_folder = "../Sound Samples/"
current_folder = base_folder + "Harp/"
volume = 1.0
current_octave = 3  # Default octave
sound_objects = {}
running = False
octave_range = [2, 3, 4, 5, 6]  # Supported octaves

key_to_note = {
    'a': "C",
    'w': "C#",
    's': "D",
    'e': "D#",
    'd': "E",
    'f': "F",
    't': "F#",
    'h': "G",
    'u': "G#",
    'j': "A",
    'i': "A#",
    'k': "B",
    'l': "C"
}

def preload_sounds():
    global sound_objects
    sound_objects = {}
    for key, note in key_to_note.items():
        if key == 'l':  # Special case for top C
            sound_file = f"{note}{current_octave + 1}.wav"
        else:
            sound_file = f"{note}{current_octave}.wav"
        sound = pygame.mixer.Sound(current_folder + sound_file)
        sound.set_volume(volume)
        sound_objects[key] = sound

def monitor_keyboard(event):
    key = event.char
    if key in sound_objects:
        sound_objects[key].play()

def start_harp():
    global running
    running = True
    preload_sounds()

    start_button.config(text="Stop", command=stop_harp)
    root.bind("<KeyPress>", monitor_keyboard)

def stop_harp():
    global running
    running = False
    start_button.config(text="Start", command=start_harp)
    root.unbind("<KeyPress>")

def adjust_volume(value):
    global volume
    volume = float(value)
    for sound in sound_objects.values():
        sound.set_volume(volume)

def choose_folder(folder_name):
    global current_folder
    current_folder = base_folder + folder_name + "/"
    if running:
        preload_sounds()

def change_octave(value):
    global current_octave
    current_octave = int(value)
    if running:
        preload_sounds()

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
