import os
import pygame
from pydub import AudioSegment
from io import BytesIO
import LLMain

# Initialize the mixer with more channels if needed
pygame.mixer.set_num_channels(64)

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
    LLMain.scheduled_tasks = {}
    LLMain.sustain_lengths = {}
    for input_key, note in LLMain.input_to_note.items():
        transposed_note, octave = transpose_note(note, LLMain.current_key)
        if input_key == '=':
            octave += 1
        sound_file = f"{transposed_note}{octave}.wav"
        sound_path = os.path.join(LLMain.current_folder, sound_file)
        sound = AudioSegment.from_wav(sound_path)

        if LLMain.sustain_option:
            # Process sound for sustain mode
            # Separate the attack and sustain portions
            attack_duration = LLMain.attack_duration
            attack = sound[:attack_duration]
            sustain = sound[attack_duration:]

            # Apply fade-in and fade-out to the sustain portion
            fade_in = LLMain.fade_in_duration
            fade_out = LLMain.fade_out_duration
            sustain = sustain.fade_in(fade_in).fade_out(fade_out)

            # Convert attack and sustain portions to pygame sounds
            attack_sound = convert_pydub_to_pygame(attack)
            sustain_sound = convert_pydub_to_pygame(sustain)

            # Set volumes
            attack_sound.set_volume(LLMain.volume)
            sustain_sound.set_volume(LLMain.volume)

            LLMain.sound_objects[input_key] = {
                'attack': attack_sound,
                'sustain': sustain_sound
            }

            # Store sustain sound length
            LLMain.sustain_lengths[input_key] = sustain_sound.get_length() * 1000  # in milliseconds

        else:
            # Load the original sound without processing
            pygame_sound = convert_pydub_to_pygame(sound)
            pygame_sound.set_volume(LLMain.volume)
            LLMain.sound_objects[input_key] = pygame_sound

# Handle key press
def key_press(event):
    key = event.char
    if key in LLMain.input_to_note and not LLMain.key_status.get(key, False):
        LLMain.key_status[key] = True

        if LLMain.sustain_option:
            sounds = LLMain.sound_objects[key]

            # After attack sound finishes, start scheduling sustain sounds
            attack_length = int(sounds['attack'].get_length() * 1000)
            LLMain.root.after(attack_length, lambda: schedule_sustain_play(key))
        else:
            # Play the original sound once
            sound = LLMain.sound_objects[key]
            sound.play()
# Schedule sustain playback with overlaps
def schedule_sustain_play(key):
    if LLMain.key_status.get(key, False):
        play_sustain_sound(key)

        # Calculate interval between sustain plays
        sustain_length = LLMain.sustain_lengths[key]
        interval = int(sustain_length / LLMain.max_overlaps)

        # Schedule the next sustain play
        task_id = LLMain.root.after(interval, lambda: schedule_sustain_play(key))
        LLMain.scheduled_tasks[key] = task_id
    else:
        task_id = LLMain.root.after(LLMain.sustain_interval, lambda: stop_sustain_sound(key))   

def play_sustain_sound(key):
    sounds = LLMain.sound_objects[key]
    sustain_sound = sounds['sustain']
    # Play sustain sound without looping
    channel = pygame.mixer.find_channel()
    if channel:
        channel.play(sustain_sound)

# Handle key release
def key_release(event):
    key = event.char
    if key in LLMain.key_status:
        LLMain.key_status[key] = False
        if LLMain.sustain_option:
            # Cancel scheduled sustain plays
            if key in LLMain.scheduled_tasks:
                LLMain.root.after_cancel(LLMain.scheduled_tasks[key])
                del LLMain.scheduled_tasks[key]
            task_id = LLMain.root.after(LLMain.sustain_interval, lambda: stop_sustain_sound(key))    

def stop_sustain_sound(key):
    # Fade out all channels playing the sustain sound for this key
    sustain_sound = LLMain.sound_objects[key]['sustain']

def start_harp():
    LLMain.running = True
    preload_sounds()

def stop_harp():
    LLMain.running = False
    pygame.mixer.stop()

# Adjust volume
def adjust_volume(value):
    LLMain.volume = float(value)
    if LLMain.sustain_option:
        for sounds in LLMain.sound_objects.values():
            sounds['attack'].set_volume(LLMain.volume)
            sounds['sustain'].set_volume(LLMain.volume)
    else:
        for sound in LLMain.sound_objects.values():
            sound.set_volume(LLMain.volume)
# Change settings
def change_octave(octave):
    LLMain.current_octave = int(octave)
    if LLMain.running:
        preload_sounds()

def choose_folder(folder_name):
    LLMain.current_folder = LLMain.base_folder + folder_name + "/"
    if LLMain.running:
        preload_sounds()

def change_key(key):
    LLMain.current_key = key
    if LLMain.running:
        preload_sounds()
