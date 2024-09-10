import os
import pygame
from pydub import AudioSegment
from io import BytesIO
import LLMain as main
import LLGui as gui

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

# Convert pydub audio to pygame sound
def convert_pydub_to_pygame(sound):
    raw_data = BytesIO()
    sound.export(raw_data, format="wav")
    raw_data.seek(0)
    return pygame.mixer.Sound(file=raw_data)

# Transpose note
def transpose_note(note, key):
    key_index = keys.index(key)
    note_index = keys.index(note)
    transposed_index = (note_index + key_index) % len(keys)
    transposed_note = keys[transposed_index]

    if transposed_index < key_index:
        return transposed_note, current_octave + 1
    return transposed_note, current_octave

# Preload sound files
def preload_sounds():
    global sound_objects
    sound_objects = {}
    
    for input_key, note in input_to_note.items():
        transposed_note, octave = transpose_note(note, current_key)
        if input_key == '=':  # Special case for top note
            octave += 1
        sound_file = f"{transposed_note}{octave}.wav"
        sound = AudioSegment.from_wav(os.path.join(current_folder, sound_file))
        pygame_sound = convert_pydub_to_pygame(sound)
        pygame_sound.set_volume(volume)
        sound_objects[input_key] = pygame_sound

# Monitor keyboard
def monitor_keyboard(event):
    global current_octave

    if event.keysym == 'Shift_R':
        if current_octave < max(octave_range):
            current_octave += 1
            preload_sounds()
    elif event.keysym == 'Shift_L':
        if current_octave > min(octave_range):
            current_octave -= 1
            preload_sounds()

    key = event.char
    if key in sound_objects:
        sound_objects[key].play()

def start_harp():
    global running
    running = True
    preload_sounds()

    gui.start_button.config(text="Stop", command=stop_harp)
    gui.root.bind("<KeyPress>", monitor_keyboard)

def stop_harp():
    global running
    running = False
    gui.start_button.config(text="Start", command=start_harp)
    gui.root.unbind("<KeyPress>")

# Change settings
def change_octave(octave):
    global current_octave
    current_octave = int(octave)
    if running:
        preload_sounds()

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

def change_key(key):
    global current_key
    current_key = key
    if running:
        preload_sounds()

# Initialize audio system
def initialize_audio():
    pygame.mixer.init()
