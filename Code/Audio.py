import pygame
from pydub import AudioSegment
from io import BytesIO
import os
import Main

# Initialize the mixer with more channels if needed
pygame.mixer.set_num_channels(64)

def convert_pydub_to_pygame(sound):
    """Convert a pydub AudioSegment to a pygame Sound object."""
    raw_data = BytesIO()
    sound.export(raw_data, format="wav")
    raw_data.seek(0)
    return pygame.mixer.Sound(file=raw_data)

def preload_sounds():
    """Preload all the sounds and process them for sustain mode."""
    Main.sound_objects = {}
    Main.sustain_lengths = {}

    for gpio_pin, note in Main.gpio_to_note.items():
        octave = Main.current_octave
        
        # Determine sound file based on current key and octave
        transposed_note, adjusted_octave = Main.transpose_note(note, Main.current_key, octave)
        sound_file = f"{transposed_note}{adjusted_octave}.wav"
        sound_path = os.path.join(Main.current_folder, sound_file)

        if not os.path.exists(sound_path):
            print(f"Sound file not found: {sound_path}")
            continue

        sound = AudioSegment.from_wav(sound_path)

        # Process sound for sustain mode
        attack_duration = Main.attack_duration
        attack = sound[:attack_duration]
        sustain = sound[attack_duration:]

        # Apply fade-in and fade-out to the sustain portion
        fade_in = Main.fade_in_duration
        fade_out = Main.fade_out_duration
        sustain = sustain.fade_in(fade_in).fade_out(fade_out)

        # Convert attack and sustain portions to pygame sounds
        attack_sound = convert_pydub_to_pygame(attack)
        sustain_sound = convert_pydub_to_pygame(sustain)

        # Set volumes
        attack_sound.set_volume(Main.volume)
        sustain_sound.set_volume(Main.volume)

        # Store sounds in the dictionary
        Main.sound_objects[note] = {
            'attack': attack_sound,
            'sustain': sustain_sound
        }

        # Store sustain sound length
        Main.sustain_lengths[note] = sustain_sound.get_length() * 1000  # in milliseconds

        # Also store the original sound for non-sustain playback
        original_sound = convert_pydub_to_pygame(sound)
        original_sound.set_volume(Main.volume)
        Main.sound_objects[note]['original'] = original_sound

def choose_folder(folder_name):
    """Change the current instrument folder and preload sounds."""
    if folder_name in Main.instrument_folders:
        Main.current_folder = os.path.join(Main.base_folder, folder_name)
        if Main.running:
            preload_sounds()
        print(f"Instrument changed to {folder_name}")
    else:
        print(f"Instrument folder {folder_name} not found.")

def adjust_volume(value):
    """Adjust the volume of all sounds."""
    Main.volume = float(value)
    for sounds in Main.sound_objects.values():
        for sound in sounds.values():
            sound.set_volume(Main.volume)

def change_octave(octave):
    """Change the current octave."""
    Main.current_octave = int(octave)
    if Main.running:
        preload_sounds()

def change_key(key):
    """Change the current key."""
    Main.current_key = key
    if Main.running:
        preload_sounds()

def start_harp():
    """Initialize and start the harp application."""
    Main.running = True
    preload_sounds()

def stop_harp():
    """Stop the harp application and clean up."""
    Main.running = False
    pygame.mixer.stop()
