import Main
import Audio
import pygame

def handle_loop_mode(note_id, key):
    """Handle looping mode for key presses."""
    if note_id in Main.looping_notes:
        stop_looping_note_by_key(note_id, key, Main.current_octave)
    else:
        if len(Main.looping_notes) >= Main.max_loops:
            print("Maximum number of looping notes reached.")
        else:
            start_looping_note(note_id, key)
    Main.loop_mode = False

def start_looping_note(note_id, key):
    """Start looping a note."""
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
        'key_locked': False,
        'locked_key': None,
        'instrument_locked': False,
        'locked_instrument': None,
        'sustain_option': Main.sustain_option,
        'active_channels': [],
        'channel': pygame.mixer.find_channel()
    }

    Main.looping_notes[note_id] = note_info
    Audio.preload_sound_for_looping_note(note_id, key, Main.current_folder)

    if Main.sustain_option:
        schedule_loop_sustain_play(key, note_id)
    else:
        schedule_normal_loop_play(key, note_id)

    Main.looping_note_slots[slot_index] = note_id
    trigger_gui_update()

def schedule_loop_sustain_play(key, note_id):
    """Schedule continuous sustain sound playback for looping."""
    if note_id in Main.looping_notes:
        note_info = Main.looping_notes[note_id]
        play_sustain_sound_loop(note_info)
        sustain_length = note_info['sustain_length']
        interval = sustain_length // Main.max_overlaps
        note_info['task_id'] = Main.root.after(interval, lambda: schedule_loop_sustain_play(key, note_id))

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

def stop_looping_note_by_key(note_id, key, octave):
    """Stop looping a note based on key and octave."""
    note_info = Main.looping_notes[note_id]
    if note_matches_current_settings(note_info, key, octave):
        stop_looping_note(note_id)

def note_matches_current_settings(note_info, key, octave):
    """Check if the pressed key and octave match the looping note."""
    expected_key = note_info['key']
    expected_octave = note_info['locked_octave'] if note_info['octave_locked'] else Main.current_octave
    return key == expected_key and octave == expected_octave

def stop_looping_note(note_id):
    """Stop looping a note."""
    if note_id in Main.looping_notes:
        note_info = Main.looping_notes.pop(note_id)
        task_id = note_info.get('task_id')
        channel = note_info.get('channel')
        slot_index = note_info['slot']

        if task_id:
            Main.root.after_cancel(task_id)

        if channel:
            channel.stop()

        for ch in note_info['active_channels']:
            ch.stop()
        note_info['active_channels'] = []

        Main.looping_note_slots[slot_index] = None
        trigger_gui_update()

def stop_all_loops():
    """Stop all looping notes."""
    for note_id in list(Main.looping_notes.keys()):
        stop_looping_note(note_id)

def lock_all_octaves():
    """Lock the octave for all looping notes."""
    for note_id, note_info in Main.looping_notes.items():
        note_info['octave_locked'] = True
        note_info['locked_octave'] = Main.current_octave
        Audio.preload_sound_for_looping_note(note_id, note_info['key'])
    trigger_gui_update()

def unlock_all_octaves():
    """Unlock the octave for all looping notes."""
    for note_id, note_info in Main.looping_notes.items():
        note_info['octave_locked'] = False
        Audio.preload_sound_for_looping_note(note_id, note_info['key'])
    trigger_gui_update()

def toggle_octave_lock(slot_index):
    """Toggle octave lock for a looping note."""
    note_id = Main.looping_note_slots[slot_index]
    if note_id:
        note_info = Main.looping_notes[note_id]
        note_info['octave_locked'] = not note_info['octave_locked']
        if note_info['octave_locked']:
            note_info['locked_octave'] = Main.current_octave
        Audio.preload_sound_for_looping_note(note_id, note_info['key'])
        trigger_gui_update()

def trigger_gui_update():
    """Trigger a GUI update."""
    if Main.advanced_menu_window and Main.advanced_menu_window.winfo_exists():
        Main.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')
