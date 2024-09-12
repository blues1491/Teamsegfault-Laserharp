import os
import pygame
from pydub import AudioSegment
from io import BytesIO
import LLMain

# Convert pydub audio to pygame sound
def convert_pydub_to_pygame(sound):
    raw_data = BytesIO()
    sound.export(raw_data, format="wav")
    raw_data.seek(0)
    return pygame.mixer.Sound(file=raw_data)

# Transpose note
def transpose_note(note, key):
    key_index = LLMain.keys.index(key)
    note_index = LLMain.keys.index(note)
    transposed_index = (note_index + key_index) % len(LLMain.keys)
    transposed_note = LLMain.keys[transposed_index]

    if transposed_index < key_index:
        return transposed_note, LLMain.current_octave + 1
    return transposed_note, LLMain.current_octave

# Preload sound files
def preload_sounds():
    LLMain.sound_objects = {}
    for input_key, note in LLMain.input_to_note.items():
        transposed_note, octave = transpose_note(note, LLMain.current_key)
        if input_key == '=':  # Special case for top note
            octave += 1
        sound_file = f"{transposed_note}{octave}.wav"
        sound_path = os.path.join(LLMain.current_folder, sound_file)
        sound = AudioSegment.from_wav(sound_path)
        if LLMain.sustain_option:
            # Apply fades and extend the sound
            fade_duration = 50  # milliseconds
            sound = sound.fade_in(fade_duration).fade_out(fade_duration)
            sound = sound * 10  # Extend sound duration
        pygame_sound = convert_pydub_to_pygame(sound)
        pygame_sound.set_volume(LLMain.volume)
        LLMain.sound_objects[input_key] = pygame_sound

# Handle key press
def key_press(event):
    key = event.char
    if key not in LLMain.key_status or not LLMain.key_status[key]:
        LLMain.key_status[key] = True
        if key in LLMain.sound_objects:
            if LLMain.sustain_option:
                LLMain.sound_objects[key].play(loops=-1)
            else:
                LLMain.sound_objects[key].play()

# Handle key release
def key_release(event):
    key = event.char
    LLMain.key_status[key] = False
    if LLMain.sustain_option and key in LLMain.sound_objects:
        LLMain.sound_objects[key].stop()

def start_harp():
    LLMain.running = True
    preload_sounds()

def stop_harp():
    LLMain.running = False

# Change settings
def change_octave(octave):
    LLMain.current_octave = int(octave)
    if LLMain.running:
        preload_sounds()

def adjust_volume(value):
    LLMain.volume = float(value)
    for sound in LLMain.sound_objects.values():
        sound.set_volume(LLMain.volume)

def choose_folder(folder_name):
    LLMain.current_folder = LLMain.base_folder + folder_name + "/"
    if LLMain.running:
        preload_sounds()

def change_key(key):
    LLMain.current_key = key
    if LLMain.running:
        preload_sounds()
