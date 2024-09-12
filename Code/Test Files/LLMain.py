import pygame
import os
import LLGui

pygame.mixer.init()

# Global Variables
running = False

base_folder = "../Sound Samples/"
current_folder = base_folder + "Harp/"
instrument_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

volume = 0.5
sound_objects = {}
key_status = {}

octave_range = [2, 3, 4, 5]
current_octave = 4

keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
current_key = "C"

fade_in_duration = 500
fade_out_duration = 500
attack_duration = 100
sustain_interval = 1000
sustain_option = False
max_overlaps = 4


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

if __name__ == "__main__":
    LLGui.main_menu()
