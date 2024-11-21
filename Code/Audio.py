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

def preload_sound_for_looping_note(note_id, key, instrument=None):
    """Preload sounds for a specific looping note."""
    note_info = Main.looping_notes[note_id]

    # Use locked instrument if applicable
    instrument_to_use = instrument or (note_info['locked_instrument'] if note_info['instrument_locked'] else Main.current_folder)
    octave = note_info['locked_octave'] if note_info['octave_locked'] else Main.current_octave
    used_key = note_info['locked_key'] if note_info['key_locked'] else Main.current_key

    print(f"Preloading sound for note {note_id}: key={used_key}, octave={octave}, instrument={instrument_to_use}")

    transposed_note, adjusted_octave = Helpers.transpose_note(Main.KEY_PINS[key], used_key, octave)
    sound_file = f"{transposed_note}{adjusted_octave}.wav"
    sound_path = os.path.join(instrument_to_use, sound_file)

    if not os.path.exists(sound_path):
        print(f"Sound file not found: {sound_path}")
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
    """Change the global instrument folder."""
    if folder_name in Main.instrument_folders:
        Main.current_folder = os.path.join(Main.base_folder, folder_name)
        print(f"Instrument changed to {folder_name}")

        if Main.running:
            preload_sounds()
            for note_id, note_info in Main.looping_notes.items():
                # Reload sounds only for unlocked notes
                if not note_info['instrument_locked']:
                    print(f"Reloading sound for unlocked note {note_id}")
                    preload_sound_for_looping_note(note_id, note_info['key'], Main.current_folder)
                else:
                    print(f"Instrument for note {note_id} remains locked to {note_info['locked_instrument']}")
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

    # Schedule GPIO polling
    def poll_wrapper():
        if Main.running:
            Main.poll_keys()
            Main.root.after(10, poll_wrapper)  # Poll every 10ms

    Main.root.after(10, poll_wrapper)  # Start polling

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

    # Clear sustain channels
    for channels in Main.active_sustain_channels.values():
        for channel in channels:
            channel.stop()
    Main.active_sustain_channels.clear()

def play_note(note_id, key, sustain_option=False):
    """Play a note with optional sustain."""
    if Main.key_status.get(key, False):  # Key already pressed
        return

    Main.key_status[key] = True  # Mark the key as pressed

    sounds = Main.sound_objects.get(key)
    if not sounds:
        print(f"No sounds loaded for key: {key}")
        return

    if sustain_option or Main.sustain_option:
        # Play attack sound and trigger sustain
        sounds['attack'].play()
        attack_length = int(sounds['attack'].get_length() * 1000)

        def sustain_play_loop():
            if Main.key_status.get(key, False):  # Ensure key is still pressed
                channel = pygame.mixer.find_channel()
                if channel:
                    channel.play(sounds['sustain'], loops=-1)  # Loop sustain
                    if key not in Main.active_sustain_channels:
                        Main.active_sustain_channels[key] = []
                    Main.active_sustain_channels[key].append(channel)

        # Schedule sustain playback
        Main.scheduled_tasks[key] = Main.root.after(attack_length, sustain_play_loop)
    else:
        # Play the original sound once
        sounds['original'].play()

def stop_sustain_sound(key):
    """Stop all channels playing the sustain sound for this key."""
    if key in Main.active_sustain_channels:
        for channel in Main.active_sustain_channels[key]:
            if Main.fade_out_duration > 0:
                channel.fadeout(Main.fade_out_duration)
            else:
                channel.stop()
        Main.active_sustain_channels[key] = []
        #print(f"Sustain sound stopped for key: {key}")

def stop_note_immediately(key):
    """Stop playback of a note immediately."""
    sounds = Main.sound_objects.get(key)
    if not sounds:
        print(f"No sounds loaded for key: {key}")
        return

    # Stop playback on all channels playing this key's sounds
    for sound_type in sounds.values():
        try:
            sound_type.stop()
        except Exception as e:
            print(f"Error stopping sound for key {key}: {e}")

    # Cancel any scheduled sustain tasks
    if key in Main.scheduled_tasks:
        Main.root.after_cancel(Main.scheduled_tasks[key])
        del Main.scheduled_tasks[key]

    # Mark the key as released
    Main.key_status[key] = False
    stop_sustain_sound(key)

def play_sustain_sound_loop(note_info):
    """Play sustain sound in a loop for a given note."""
    key = note_info['key']
    sounds = Main.sound_objects.get(key)
    if not sounds:
        print(f"No sounds loaded for key: {key}")
        return

    sustain_sound = sounds['sustain']
    channel = pygame.mixer.find_channel()
    if channel:
        channel.play(sustain_sound, loops=-1)
        note_info['active_channels'].append(channel)


def play_sustain_sound(key):
    """Play sustain sound in a loop for the given key."""
    sounds = Main.sound_objects.get(key)
    if not sounds:
        print(f"No sounds loaded for key: {key}")
        return

    sustain_sound = sounds['sustain']
    channel = pygame.mixer.find_channel()
    if channel:
        channel.play(sustain_sound, loops=-1)  # Loop the sustain sound
        if key not in Main.active_sustain_channels:
            Main.active_sustain_channels[key] = []
        Main.active_sustain_channels[key].append(channel)
        print(f"Sustain sound started for key: {key}")

