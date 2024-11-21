import os
import Helpers
import Main
import Audio
import pygame

def handle_loop_mode(note_id, key):
    """Handle looping mode for key presses."""
    
    if len(Main.looping_notes) >= Main.max_loops:
        print("Maximum number of looping notes reached.")
    else:
        start_looping_note(note_id, key)
    Main.loop_mode = False

def start_looping_note(note_id, key):
    """Start looping a note and assign it to an available slot."""
    try:
        slot_index = Main.looping_note_slots.index(None)
    except ValueError:
        print("No available looping note slots.")
        return

    note_info = {
        'key': key,
        'slot': slot_index,
        'octave_locked': False,
        'locked_octave': Main.current_octave,
        'sustain_option': Main.sustain_option,
        'key_locked': False,
        'locked_key': key,
        'instrument_locked': False,
        'locked_instrument': Main.current_folder,
        'active_channels': [],
        'channel': pygame.mixer.find_channel(),
    }

    Main.looping_notes[note_id] = note_info

    # Use locked instrument if applicable
    instrument_to_use = (
        note_info['locked_instrument'] if note_info['instrument_locked'] else Main.current_folder
    )
    Audio.preload_sound_for_looping_note(note_id, key, instrument=instrument_to_use)

    if Main.sustain_option:
        schedule_loop_sustain_play(key, note_id)
    else:
        schedule_normal_loop_play(key, note_id)

    Main.looping_note_slots[slot_index] = note_id
    trigger_gui_update()

def schedule_loop_sustain_play(key, note_id):
    """Schedule sustain playback for a looping note."""
    note_info = Main.looping_notes[note_id]

    # Determine the instrument to use
    instrument = note_info['locked_instrument'] if note_info['instrument_locked'] else Main.current_folder

    # Ensure sounds are preloaded for the correct instrument
    Audio.preload_sound_for_looping_note(note_id, key, instrument=instrument)

    # Define the sustain playback loop
    def play_sustain():
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(note_info['sounds']['sustain'], loops=-1)  # Loop sustain
            note_info['active_channels'].append(channel)

    # Schedule sustain playback
    play_sustain()


def play_sustain_sound_loop(note_info):
    """Play the sustain sound for a looping note."""
    sustain_sound = note_info['sounds']['sustain']
    channel = pygame.mixer.find_channel()
    if channel:
        channel.play(sustain_sound)
        note_info['active_channels'].append(channel)

def schedule_normal_loop_play(key, note_id):
    """Schedule normal looping playback."""
    if note_id in Main.looping_notes:
        note_info = Main.looping_notes[note_id]
        channel = note_info['channel']
        sounds = note_info['sounds']
        channel.play(sounds['original'])
        sound_length = int(sounds['original'].get_length() * 1000)
        note_info['task_id'] = Main.root.after(sound_length, lambda: schedule_normal_loop_play(key, note_id))

def stop_looping_note(note_id):
    """Stop looping a note and free its slot."""
    if note_id in Main.looping_notes:
        note_info = Main.looping_notes.pop(note_id)
        task_id = note_info.get('task_id')
        if task_id:
            Main.root.after_cancel(task_id)
        for channel in note_info.get('active_channels', []):
            channel.stop()
        Main.looping_note_slots[note_info['slot']] = None
        trigger_gui_update()

def stop_all_loops():
    """Stop all looping notes."""
    for note_id in list(Main.looping_notes.keys()):
        stop_looping_note(note_id)
        
def trigger_gui_update():
    """Trigger a GUI update."""
    if Main.advanced_menu_window and Main.advanced_menu_window.winfo_exists():
        Main.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def unlock_key_and_octave(note_id):
    """Unlock the key for a specific looping note."""
    note_info = Main.looping_notes[note_id]
    note_info['key_locked'] = False
    print(f"Unlocked key for note {note_id}. Adjusting to current key.")

    # Convert current and locked keys to indices for transposition
    locked_key_index = Helpers.key_to_index(note_info['locked_key'])
    current_key_index = Helpers.key_to_index(Main.current_key)
    current_transposition = current_key_index - locked_key_index

    # Update the locked key and adjust the looping note's key
    note_info['locked_key'] = Main.current_key
    note_info['key'] = (note_info['key'] + current_transposition) % len(Main.keys)

    # Convert the updated key to its corresponding GPIO pin
    note_name = Main.keys[note_info['key']]
    gpio_pin = Helpers.note_to_gpio(note_name)  # Map note to GPIO pin

    # Preload sound with the correct GPIO pin
    Audio.preload_sound_for_looping_note(note_id, gpio_pin, instrument=note_info['locked_instrument'])

    # Update the GUI
    trigger_gui_update()

def stop_looping(note_id):
    """Stop a specific looping note."""
    if note_id in Main.looping_notes:
        stop_looping_note(note_id)
        trigger_gui_update()
