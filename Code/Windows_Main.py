import pygame
import threading
import tkinter as tk
from tkinter import ttk, filedialog

# Initialize pygame mixer without initializing the video system
pygame.mixer.init()

# Global variables for settings
current_folder = "Sound Samples/Harp/"
volume = 1.0
current_octave = 3  # Default octave
sound_objects = {}  # Dictionary to store sound objects
running = False  # Flag to check if the harp is running
octave_range = [2, 3, 4, 5, 6]  # Supported octaves

key_to_note = {
    '`': "C",
    '1': "C#",
    '2': "D",
    '3': "D#",
    '4': "E",
    '5': "F",
    '6': "F#",
    '7': "G",
    '8': "G#",
    '9': "A",
    '0': "A#",
    '-': "B",
    '=': "C"
}

def preload_sounds():
    """Preload all sound files to ensure they are ready for playback."""
    global sound_objects
    sound_objects = {}
    for key, note in key_to_note.items():
        if key == '=':  # Special case for top C
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
    root.bind("<KeyPress>", monitor_keyboard)  # Bind key press events

def stop_harp():
    global running
    running = False
    start_button.config(text="Start", command=start_harp)
    root.unbind("<KeyPress>")  # Unbind key press events

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

def change_octave(value):
    global current_octave
    current_octave = int(value)
    if running:
        stop_harp()
        start_harp()

def open_main_menu():
    global start_button
    global root
    root = tk.Tk()
    root.title("Laser Harp Main Menu")

    ttk.Label(root, text="Laser Harp", font=("Helvetica", 16)).pack(pady=20)

    start_button = ttk.Button(root, text="Start", command=start_harp)
    start_button.pack(pady=10)

    ttk.Button(root, text="Settings", command=open_settings).pack(pady=10)
    ttk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    root.mainloop()

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Settings")

    ttk.Label(settings_window, text="Adjust Volume").pack(pady=10)
    volume_slider = ttk.Scale(settings_window, from_=0, to=1, orient='horizontal', command=adjust_volume)
    volume_slider.set(volume)
    volume_slider.pack(pady=10)

    ttk.Label(settings_window, text="Select Octave").pack(pady=10)
    octave_dropdown = ttk.Combobox(settings_window, values=octave_range)
    octave_dropdown.set(current_octave)
    octave_dropdown.bind("<<ComboboxSelected>>", lambda e: change_octave(octave_dropdown.get()))
    octave_dropdown.pack(pady=10)

    ttk.Button(settings_window, text="Change Instrument Folder", command=choose_folder).pack(pady=10)

    settings_window.mainloop()

if __name__ == "__main__":
    open_main_menu()
