# LLMain.py

import lgpio
import time
import os
import pygame
import Gui
import Audio
import Helpers
import Looping

# Initialize Pygame mixer
pygame.mixer.init()

# Global Variables
running = False

# Paths and Folders
base_folder = "Sound Samples/"
current_folder = os.path.join(base_folder, "Harp")
instrument_folders = [
    f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))
]

# Audio Settings
volume = 0.5
sound_objects = {}
sustain_lengths = {}

# Key Mappings and Notes
KEY_PINS = {
    21: "C",    # GPIO pin 17 -> "C"
    20: "C#",   # GPIO pin 18 -> "C#"
    16: "D",    # GPIO pin 27 -> "d"
    12: "D#",   # GPIO pin 22 -> "D#"
    25: "E",    # GPIO pin 23 -> "E"
    24: "F",    # GPIO pin 24 -> "F"
    23: "F#",   # GPIO pin 25 -> "F#"
    18: "G",     # GPIO pin 5 -> "G"
    26: "G#",    # GPIO pin 6 -> "G#"
    19: "A",    # GPIO pin 12 -> "A"
    13: "A#",   # GPIO pin 13 -> "A#"
    6: "B",    # GPIO pin 19 -> "B"
    5: "C"    # GPIO pin 26 -> "C2"
}
keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
current_key = "C"

# Octave Settings
octave_range = [2, 3, 4, 5]
current_octave = 3

# Sustain and Overlap Settings
fade_in_duration = 500    # milliseconds
fade_out_duration = 500   # milliseconds
attack_duration = 100     # milliseconds
sustain_interval = 1000   # milliseconds
sustain_option = False
max_overlaps = 10

# Looping Notes Settings
loop_mode = False         # Indicates if loop mode is active
max_loops = 5            # Maximum number of looping notes
looping_notes = {}
looping_note_slots = [None] * max_loops  # Initialize slots based on max_loops

# GUI and Event Handling
root = None
advanced_menu_window = None  # Reference to the advanced menu window

# Key Status and Scheduling
key_status = {pin: False for pin in KEY_PINS}  # Track which keys are active
last_press_time = {pin: 0 for pin in KEY_PINS}  # For debounce
scheduled_tasks = {}

# Shift Key Timing for Octave Changes
last_shift_l_time = 0
last_shift_r_time = 0
shift_cooldown = 0.2  # 200 milliseconds

# Initialize sustain channel tracking
active_sustain_channels = {pin: [] for pin in KEY_PINS}

# Add debounce time
DEBOUNCE_TIME = 0.1  # 100ms

# Initialize GPIO chip
# Initialize GPIO chip
chip = lgpio.gpiochip_open(0)

# Ensure pins are claimed only once
claimed_pins = set()

for pin in KEY_PINS:
    if pin not in claimed_pins:
        try:
            lgpio.gpio_claim_input(chip, pin)
            claimed_pins.add(pin)
            print(f"Claimed GPIO pin: {pin}")
        except lgpio.error as e:
            if "GPIO busy" in str(e):
                print(f"GPIO pin {pin} is already in use. Skipping...")
            else:
                raise

def handle_key_press(note):
    """Handle key press logic."""
    #print(f"Key pressed: {note}")
    octave = current_octave
    if KEY_PINS[note] == 5:  # Example for octave change
        octave += 1
    note_id = Helpers.get_note_identifier(note, octave)

    if loop_mode:
        Looping.handle_loop_mode(note_id, note)  # Activate looping logic
    else:
        Audio.play_note(note_id, note, sustain_option)  # Play normal sound

def handle_key_release(note):
    """Handle key release logic."""
    key_status[note] = False  # Mark key as released
    if sustain_option:
        Audio.stop_sustain_sound(note)  # Stop sustain if active
    else:
        Audio.stop_note_immediately(note)  # Stop normal playback

def poll_keys():
    """Poll GPIO pins for state changes."""
    for pin in claimed_pins:  # Use only successfully claimed pins
        try:
            pin_state = lgpio.gpio_read(chip, pin)
            if pin_state == 1:  # Detect key press
                handle_key_press(pin)
            elif pin_state == 0:  # Detect key release
                handle_key_release(pin)
        except lgpio.error as e:
            print(f"Error reading GPIO pin {pin}: {e}")

def cleanup_gpio():
    """Release GPIO pins on exit."""
    for pin in claimed_pins:
        try:
            lgpio.gpio_free(chip, pin)
        except lgpio.error as e:
            print(f"Error releasing GPIO pin {pin}: {e}")
    lgpio.gpiochip_close(chip)

if __name__ == "__main__":
    Gui.main_menu()  # Launch the GUI
