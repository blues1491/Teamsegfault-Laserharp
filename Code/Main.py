import lgpio
import pygame
import os

# Initialize Pygame mixer
pygame.mixer.init()

# Global Variables
running = False

# Paths and Folders
base_folder = "../Sound Samples/"
current_folder = os.path.join(base_folder, "Harp")
instrument_folders = [
    f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))
]

# Audio Settings
volume = 0.5
sound_objects = {}
sustain_lengths = {}

# GPIO Mappings and Notes
gpio_to_note = {
    17: "C",
    18: "C#",
    27: "D",
    22: "D#",
    23: "E",
    24: "F",
    25: "F#",
    5: "G",
    6: "G#",
    12: "A",
    13: "A#",
    19: "B",
    16: "C"
}
keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
current_key = "C"

# Octave Settings
octave_range = [2, 3, 4, 5]
current_octave = 3

# Sustain and GPIO Sustain Settings
fade_in_duration = 500    # milliseconds
fade_out_duration = 500   # milliseconds
attack_duration = 100     # milliseconds
sustain_interval = 1000   # milliseconds
sustain_option = False
sustain_gpio_pin = 21  # GPIO pin for sustain toggle

# GUI and Event Handling
root = None

# Key Status and Scheduling
key_status = {}
scheduled_tasks = {}

# GPIO Initialization
chip = lgpio.gpiochip_open(0)
for pin in gpio_to_note.keys():
    lgpio.gpio_claim_input(chip, pin)
lgpio.gpio_claim_input(chip, sustain_gpio_pin)

def read_gpio_inputs():
    """Check the state of GPIO pins and play corresponding notes."""
    global sustain_option
    for pin, note in gpio_to_note.items():
        if lgpio.gpio_read(chip, pin) == 1:  # Pin is HIGH
            if not key_status.get(pin, False):  # If note is not already playing
                play_note(note)
                key_status[pin] = True
        else:  # Pin is LOW
            if key_status.get(pin, False):  # If note was playing
                stop_note(note)
                key_status[pin] = False

    # Handle sustain toggle
    sustain_option = lgpio.gpio_read(chip, sustain_gpio_pin) == 1

def play_note(note):
    """Play a note using the sound object."""
    if sustain_option:
        sounds = sound_objects[note]
        sounds['attack'].play()
        attack_length = int(sounds['attack'].get_length() * 1000)
        root.after(attack_length, lambda: schedule_sustain_play(note))
    else:
        sounds = sound_objects[note]
        sounds['original'].play()

def stop_note(note):
    """Stop playing a note."""
    if sustain_option:
        if note in scheduled_tasks:
            root.after_cancel(scheduled_tasks[note])
            del scheduled_tasks[note]

def schedule_sustain_play(note):
    """Schedule the sustain sound to play."""
    if key_status.get(note, False):  # Only if the note is still active
        sounds = sound_objects[note]
        sounds['sustain'].play()

def start_harp():
    """Start the harp application."""
    global running
    running = True
    preload_sounds()
    while running:
        read_gpio_inputs()

def stop_harp():
    """Stop the harp application."""
    global running
    running = False
    pygame.mixer.stop()

def preload_sounds():
    """Preload sounds for the current instrument."""
    # Logic for preloading sounds based on current folder and settings.

# Debounce handling can be added if needed for noisy GPIO pins.

# Start the main program loop if this file is executed directly.
if __name__ == "__main__":
    start_harp()
