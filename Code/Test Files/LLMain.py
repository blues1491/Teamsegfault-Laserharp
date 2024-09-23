import pygame
import os
import LLGui 

pygame.mixer.init()

# Global Variables
running = False

base_folder = "../Sound Samples/"
current_folder = base_folder + "Harp/"
instrument_folders = [
    f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))
]

volume = 0.5
sound_objects = {}
key_status = {}
sustain_lengths = {}
scheduled_tasks = {}
looping_notes = {}

octave_range = [2, 3, 4, 5]
current_octave = 4

keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
current_key = "C"

fade_in_duration = 500    # milliseconds
fade_out_duration = 500   # milliseconds
attack_duration = 100     # milliseconds
sustain_interval = 1000   # milliseconds
sustain_option = False
max_overlaps = 5

# New Global Variables for Looping Functionality
loop_mode = False         # Indicates if loop mode is active
max_loops = 5             # Maximum number of looping notes

input_to_note = {
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

root = None

# New variables to track the time of the last shift key press
last_shift_l_time = 0
last_shift_r_time = 0

# Define a cooldown period in seconds
shift_cooldown = 0.2  # 200 milliseconds

if __name__ == "__main__":
    LLGui.main_menu()
