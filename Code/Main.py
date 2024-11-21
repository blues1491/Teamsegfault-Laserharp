# LLMain.py

import lgpio
import time
import os
import pygame
import Gui
import Audio
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
    17: "C",    # GPIO pin 17 -> "C"
    18: "C#",   # GPIO pin 18 -> "C#"
    27: "D",    # GPIO pin 27 -> "D"
    22: "D#",   # GPIO pin 22 -> "D#"
    23: "E",    # GPIO pin 23 -> "E"
    24: "F",    # GPIO pin 24 -> "F"
    25: "F#",   # GPIO pin 25 -> "F#"
    5: "G",     # GPIO pin 5 -> "G"
    6: "G#",    # GPIO pin 6 -> "G#"
    12: "A",    # GPIO pin 12 -> "A"
    13: "A#",   # GPIO pin 13 -> "A#"
    19: "B",    # GPIO pin 19 -> "B"
    26: "C"    # GPIO pin 26 -> "C2"
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
max_overlaps = 8

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

# Store active channels for sustain sounds
active_sustain_channels = {}

# Add debounce time
DEBOUNCE_TIME = 0.1  # 100ms

# Initialize GPIO chip
chip = lgpio.gpiochip_open(0)
for pin in KEY_PINS:
    lgpio.gpio_claim_input(chip, pin)

def handle_key_press(note):
    """Handle key press logic."""
    print(f"Key pressed: {note}")
    octave = current_octave
    if note == "C2":  # Example for octave change
        octave += 1
    note_id = Audio.get_note_identifier(note, octave)

    if loop_mode:
        Looping.handle_loop_mode(note_id, note)  # Activate looping logic
    else:
        Audio.play_note(note_id, note, sustain_option)  # Play normal sound

def handle_key_release(note):
    """Handle key release logic."""
    print(f"Key released: {note}")
    if sustain_option:
        Audio.stop_sustain(note)  # Stop sustain if active
    else:
        Audio.stop_note_immediately(note)  # Stop normal playback

def poll_keys():
    """Poll GPIO pins to detect keypresses and handle logic."""
    current_time = time.time()
    for pin, note in KEY_PINS.items():
        pin_state = lgpio.gpio_read(chip, pin)
        if pin_state == 1:  # Button pressed (GPIO HIGH)
            if not key_status[pin] and (current_time - last_press_time[pin] > DEBOUNCE_TIME):
                key_status[pin] = True
                last_press_time[pin] = current_time
                handle_key_press(note)  # Process key press
        else:  # Button released (GPIO LOW)
            if key_status[pin]:
                key_status[pin] = False
                handle_key_release(note)  # Process key release

def main():
    """Main loop for polling GPIO and running the GUI."""
    global running
    running = True

    # Preload audio and start GUI
    Audio.preload_sounds()

    try:
        while True:
            poll_keys()  # Check GPIO inputs
            time.sleep(0.01)  # Small delay for CPU relief
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        running = False
        lgpio.gpiochip_close(chip)  # Cleanup GPIO
        pygame.mixer.quit()

if __name__ == "__main__":
    Gui.main_menu()  # Launch the GUI
    main()
