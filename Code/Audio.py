# Audio.py

import pygame
from pydub import AudioSegment
from io import BytesIO
import os
import Main
import Helpers

# Initialize the mixer with more channels if needed
pygame.mixer.set_num_channels(64)

def convert_pydub_to_pygame(sound):
    """Convert a pydub AudioSegment to a pygame Sound object."""
    raw_data = BytesIO()
    sound.export(raw_data, format="wav")
    raw_data.seek(0)
    return pygame.mixer.Sound(file=raw_data)

def preload_sounds():
    """Preload sounds for sustain and looping modes."""
    Main.sound_objects = {}
    Main.sustain_lengths = {}

    for pin, note in Main.KEY_PINS.items():
        octave = Main.current_octave
        if pin == 26:  # Example pin for octave shift
            octave += 1

        transposed_note, adjusted_octave = Helpers.transpose_note(note, Main.current_key, octave)
        sound_file = f"{transposed_note}{adjusted_octave}.wav"
        sound_path = os.path.join(Main.current_folder, sound_file)

        if not os.path.exists(sound_path):
            print(f"Sound file not found: {sound_path}")
            continue

        sound = AudioSegment.from_wav(sound_path)
        attack = sound[:Main.attack_duration]
        sustain = sound[Main.attack_duration:].fade_in(Main.fade_in_duration).fade_out(Main.fade_out_duration)

        attack_sound = convert_pydub_to_pygame(attack)
        sustain_sound = convert_pydub_to_pygame(sustain)
        original_sound = convert_pydub_to_pygame(sound)

        for s in [attack_sound, sustain_sound, original_sound]:
            s.set_volume(Main.volume)

        Main.sound_objects[pin] = {
            'attack': attack_sound,
            'sustain': sustain_sound,
            'original': original_sound
        }
        Main.sustain_lengths[pin] = sustain_sound.get_length() * 1000

    # Trigger GUI updates
    if Main.advanced_menu_window and Main.advanced_menu_window.winfo_exists():
        Main.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def preload_sound_for_looping_note(note_id, key, instrument):
    """Preload sounds for a specific looping note."""
    note_info = Main.looping_notes[note_id]
    octave = note_info['locked_octave'] if note_info['octave_locked'] else Main.current_octave
    used_key = note_info['locked_key'] if note_info['key_locked'] else Main.current_key
    instrument_folder = note_info['locked_instrument'] if note_info['instrument_locked'] else Main.current_folder

    transposed_note, adjusted_octave = Helpers.transpose_note(Main.input_to_note[key], used_key, octave)
    sound_file = f"{transposed_note}{adjusted_octave}.wav"
    sound_path = os.path.join(instrument_folder, sound_file)

    if not os.path.exists(sound_path):
        print(f"Sound file not found for looping note: {sound_path}")
        return

    sound = AudioSegment.from_wav(sound_path)
    attack = sound[:Main.attack_duration]
    sustain = sound[Main.attack_duration:].fade_in(Main.fade_in_duration).fade_out(Main.fade_out_duration)

    attack_sound = convert_pydub_to_pygame(attack)
    sustain_sound = convert_pydub_to_pygame(sustain)
    original_sound = convert_pydub_to_pygame(sound)

    for s in [attack_sound, sustain_sound, original_sound]:
        s.set_volume(Main.volume)

    note_info['sounds'] = {
        'attack': attack_sound,
        'sustain': sustain_sound,
        'original': original_sound
    }
    note_info['sustain_length'] = sustain_sound.get_length() * 1000

def choose_folder(folder_name):
    """Change the instrument folder and reload sounds."""
    if folder_name in Main.instrument_folders:
        Main.current_folder = os.path.join(Main.base_folder, folder_name)
        if Main.running:
            preload_sounds()
            for note_id, note_info in Main.looping_notes.items():
                if not note_info.get('instrument_locked'):
                    preload_sound_for_looping_note(note_id, note_info['key'], Main.current_folder)
        print(f"Instrument changed to {folder_name}")
    else:
        print(f"Instrument folder {folder_name} not found.")

def adjust_volume(value):
    """Adjust the playback volume."""
    Main.volume = float(value)
    for sounds in Main.sound_objects.values():
        for sound in sounds.values():
            sound.set_volume(Main.volume)
    for note_info in Main.looping_notes.values():
        for sound in note_info.get('sounds', {}).values():
            sound.set_volume(Main.volume)

def change_octave(octave):
    """Change the current octave and reload sounds."""
    Main.current_octave = int(octave)
    if Main.running:
        preload_sounds()
    if Main.advanced_menu_window and Main.advanced_menu_window.winfo_exists():
        Main.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def change_key(key):
    """Change the current key and reload sounds."""
    Main.current_key = key
    if Main.running:
        preload_sounds()
    if Main.advanced_menu_window and Main.advanced_menu_window.winfo_exists():
        Main.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def start_harp():
    """Start the harp application."""
    Main.running = True
    preload_sounds()

def stop_harp():
    """Stop the harp application."""
    Main.running = False
    pygame.mixer.stop()
    for note_id in list(Main.looping_notes.keys()):
        import Looping
        Looping.stop_looping_note(note_id)
    for key in list(Main.scheduled_tasks.keys()):
        Main.root.after_cancel(Main.scheduled_tasks[key])
    Main.scheduled_tasks.clear()
