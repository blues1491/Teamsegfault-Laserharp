# LLLooping.py

import LLMain
import LLAudio
import LLHelpers
import pygame
import time

def key_press(event):
    """Handle key press events."""
    keysym = event.keysym
    key = event.char
    current_time = time.time()

    if keysym == 'Shift_L':
        handle_shift('left', current_time)
    elif keysym == 'Shift_R':
        handle_shift('right', current_time)
    elif key in LLMain.input_to_note:
        octave = LLMain.current_octave
        if key == '=':
            octave += 1
        note_id = LLHelpers.get_note_identifier(key, octave)
        if LLMain.loop_mode:
            handle_loop_mode(note_id, key)
        else:
            handle_normal_key_press(note_id, key)

def handle_shift(direction, current_time):
    """Handle octave changes with shift keys."""
    if direction == 'left':
        if current_time - LLMain.last_shift_l_time > LLMain.shift_cooldown:
            new_octave = LLMain.current_octave - 1
            if new_octave in LLMain.octave_range:
                LLAudio.change_octave(new_octave)
                LLMain.last_shift_l_time = current_time
                print(f"Octave decreased to {new_octave}")
            else:
                print("Cannot decrease octave further.")
    elif direction == 'right':
        if current_time - LLMain.last_shift_r_time > LLMain.shift_cooldown:
            new_octave = LLMain.current_octave + 1
            if new_octave in LLMain.octave_range:
                LLAudio.change_octave(new_octave)
                LLMain.last_shift_r_time = current_time
                print(f"Octave increased to {new_octave}")
            else:
                print("Cannot increase octave further.")

def handle_loop_mode(note_id, key):
    """Handle looping mode key presses."""
    if note_id in LLMain.looping_notes:
        # Note is already looping, stop looping it
        stop_looping_note_by_key(note_id)
    else:
        # Check if max loops reached
        if len(LLMain.looping_notes) >= LLMain.max_loops:
            print("Maximum number of looping notes reached.")
        else:
            # Start looping the note
            start_looping_note(note_id, key)
    # Reset loop mode
    LLMain.loop_mode = False
    print("Loop mode deactivated.")

def handle_normal_key_press(note_id, key):
    """Handle normal key presses."""
    if note_id in LLMain.looping_notes:
        # Stop the looping note
        stop_looping_note_by_key(note_id)
    else:
        if not LLMain.key_status.get(key, False):
            LLMain.key_status[key] = True
            if LLMain.sustain_option:
                # Play attack sound, then schedule sustain playback
                sounds = LLMain.sound_objects[key]
                sounds['attack'].play()
                attack_length = int(sounds['attack'].get_length() * 1000)
                LLMain.root.after(attack_length, lambda: schedule_sustain_play(key))
            else:
                # Play the original sound once
                sounds = LLMain.sound_objects[key]
                sounds['original'].play()

def key_release(event):
    """Handle key release events."""
    key = event.char
    keysym = event.keysym

    if key in LLMain.input_to_note:
        if key in LLMain.key_status:
            LLMain.key_status[key] = False
            octave = LLMain.current_octave
            if key == '=':
                octave += 1
            note_id = LLHelpers.get_note_identifier(key, octave)
            if LLMain.sustain_option:
                # If the note is looping, do not stop it
                if note_id in LLMain.looping_notes:
                    pass
                else:
                    # Cancel scheduled sustain plays
                    if key in LLMain.scheduled_tasks:
                        LLMain.root.after_cancel(LLMain.scheduled_tasks[key])
                        del LLMain.scheduled_tasks[key]
                    # Schedule to stop the sustain sound after sustain_interval
                    task_id = LLMain.root.after(LLMain.sustain_interval, lambda: stop_sustain_sound(key))
                    LLMain.scheduled_tasks[key] = task_id

def schedule_sustain_play(key):
    """Schedule the sustain sound to play with overlaps."""
    if LLMain.key_status.get(key, False):
        play_sustain_sound(key)

        # Calculate interval between sustain plays
        sustain_length = LLMain.sustain_lengths[key]
        interval = int(sustain_length / LLMain.max_overlaps)

        # Schedule the next sustain play
        task_id = LLMain.root.after(interval, lambda: schedule_sustain_play(key))
        LLMain.scheduled_tasks[key] = task_id
    else:
        # If the key is no longer pressed, schedule to stop the sustain sound
        task_id = LLMain.root.after(LLMain.sustain_interval, lambda: stop_sustain_sound(key))
        LLMain.scheduled_tasks[key] = task_id

def play_sustain_sound(key):
    """Play the sustain sound once, without looping."""
    sounds = LLMain.sound_objects[key]
    sustain_sound = sounds['sustain']
    # Play sustain sound without looping
    channel = pygame.mixer.find_channel()
    if channel:
        channel.play(sustain_sound)

def stop_sustain_sound(key):
    """Fade out all channels playing the sustain sound for this key."""
    octave = LLMain.current_octave
    if key == '=':
        octave += 1
    note_id = LLHelpers.get_note_identifier(key, octave)
    if note_id in LLMain.looping_notes:
        # Do not stop the sound if it's looping
        return

    sustain_sound = LLMain.sound_objects[key]['sustain']
    for task_info in LLMain.looping_notes.values():
        channel = task_info.get('channel')
        if channel and channel.get_sound() == sustain_sound:
            if LLMain.fade_out_duration > 0:
                channel.fadeout(LLMain.fade_out_duration)
            else:
                channel.stop()

    # Remove scheduled stop
    if key in LLMain.scheduled_tasks:
        del LLMain.scheduled_tasks[key]

def start_looping_note(note_id, key):
    """Start looping a note and assign it to an available slot."""
    # Find an available slot
    try:
        slot_index = LLMain.looping_note_slots.index(None)
    except ValueError:
        print("No available looping note slots.")
        return

    # Store whether the octave is locked for this note (default to False)
    octave_locked = False
    locked_octave = LLMain.current_octave

    # Create the note_info dictionary
    note_info = {
        'key': key,
        'slot': slot_index,
        'octave_locked': octave_locked,
        'locked_octave': locked_octave,
        'sustain_option': LLMain.sustain_option  # Store sustain option status
    }

    # Add note_info to looping_notes
    LLMain.looping_notes[note_id] = note_info

    # Preload the sound for this looping note
    LLAudio.preload_sound_for_looping_note(note_id, key)

    # Now get the sounds from note_info
    sounds = note_info.get('sounds', {})
    if not sounds:
        print(f"Failed to load sounds for looping note: {note_id}")
        del LLMain.looping_notes[note_id]
        LLMain.looping_note_slots[slot_index] = None
        return

    if LLMain.sustain_option:
        # Play the attack sound and schedule sustain playbacks
        sounds['attack'].play()
        attack_length = int(sounds['attack'].get_length() * 1000)
        task_id = LLMain.root.after(attack_length, lambda: schedule_loop_sustain_play(key, note_id))
        channel = pygame.mixer.find_channel()
        print(f"Started looping note with sustain: {note_id}")
    else:
        # Play the original sound back to back without sustain settings
        channel = pygame.mixer.find_channel()
        task_id = LLMain.root.after(0, lambda: schedule_normal_loop_play(key, note_id))
        print(f"Started looping note normally: {note_id}")

    # Update note_info with task_id and channel
    note_info['task_id'] = task_id
    note_info['channel'] = channel

    # Update the looping note slot
    LLMain.looping_note_slots[slot_index] = note_id

    # Update the GUI display if advanced menu is open
    if LLMain.advanced_menu_window and LLMain.advanced_menu_window.winfo_exists():
        LLMain.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def schedule_normal_loop_play(key, note_id):
    """Schedule the next playback of the original sound for normal looping."""
    if note_id in LLMain.looping_notes:
        note_info = LLMain.looping_notes[note_id]
        sounds = note_info['sounds']
        channel = note_info['channel']
        channel.play(sounds['original'])
        sound_length = int(sounds['original'].get_length() * 1000)
        task_id = LLMain.root.after(sound_length, lambda: schedule_normal_loop_play(key, note_id))
        note_info['task_id'] = task_id
    else:
        # If the note is no longer looping, do nothing
        pass

def schedule_loop_sustain_play(key, note_id):
    """Schedule the sustain sound to play with overlaps for looping."""
    if note_id in LLMain.looping_notes:
        note_info = LLMain.looping_notes[note_id]
        play_sustain_sound_loop(note_info)
        # Calculate interval between sustain plays
        sustain_length = note_info['sustain_length']
        interval = int(sustain_length / LLMain.max_overlaps)
        # Schedule the next sustain play
        task_id = LLMain.root.after(interval, lambda: schedule_loop_sustain_play(key, note_id))
        note_info['task_id'] = task_id
    else:
        # If note is no longer looping, do nothing
        pass

def play_sustain_sound_loop(note_info):
    """Play the sustain sound for a looping note."""
    sustain_sound = note_info['sounds']['sustain']
    # Play sustain sound without looping
    channel = pygame.mixer.find_channel()
    if channel:
        channel.play(sustain_sound)

def stop_looping_note_by_key(note_id):
    """Stop looping a note when the user plays the note again."""
    stop_looping_note(note_id)
    print(f"Stopped looping note by key press: {note_id}")

def stop_looping_note(note_id):
    """Stop looping a note and free its slot."""
    if note_id in LLMain.looping_notes:
        # Retrieve note info
        note_info = LLMain.looping_notes[note_id]
        task_id = note_info.get('task_id')
        channel = note_info.get('channel')
        slot_index = note_info.get('slot')

        if task_id:
            LLMain.root.after_cancel(task_id)

        if channel:
            if LLMain.fade_out_duration > 0:
                channel.fadeout(LLMain.fade_out_duration)
            else:
                channel.stop()

        # Remove looping note
        del LLMain.looping_notes[note_id]

        # Free the slot
        LLMain.looping_note_slots[slot_index] = None

        # Update the GUI display
        if LLMain.advanced_menu_window and LLMain.advanced_menu_window.winfo_exists():
            LLMain.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

        print(f"Stopped looping note: {note_id}")
    else:
        print(f"Note {note_id} is not currently looping.")

def stop_loop_by_slot(slot_index):
    """Stop a looping note by its slot index."""
    note_id = LLMain.looping_note_slots[slot_index]
    if note_id:
        stop_looping_note(note_id)
        print(f"Stopped looping note in slot {slot_index + 1}: {note_id}")
    else:
        print(f"No looping note in slot {slot_index + 1} to stop.")

def stop_all_loops():
    """Stop all looping notes."""
    for note_id in list(LLMain.looping_notes.keys()):
        stop_looping_note(note_id)
    print("All looping notes have been stopped.")

def toggle_octave_lock(slot_index):
    """Toggle the octave lock for a looping note in a given slot."""
    note_id = LLMain.looping_note_slots[slot_index]
    if note_id:
        note_info = LLMain.looping_notes[note_id]
        note_info['octave_locked'] = not note_info['octave_locked']
        if note_info['octave_locked']:
            note_info['locked_octave'] = LLMain.current_octave
            print(f"Octave locked for note {note_id} at octave {note_info['locked_octave']}")
            # Reload sound with the locked octave
            LLAudio.preload_sound_for_looping_note(note_id, note_info['key'])
        else:
            print(f"Octave unlocked for note {note_id}")
            # Reload sound with the current global octave
            LLAudio.preload_sound_for_looping_note(note_id, note_info['key'])
        # Update the GUI display
        if LLMain.advanced_menu_window and LLMain.advanced_menu_window.winfo_exists():
            LLMain.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def lock_all_octaves():
    """Lock the octave for all looping notes."""
    for note_id, note_info in LLMain.looping_notes.items():
        if not note_info['octave_locked']:
            note_info['octave_locked'] = True
            note_info['locked_octave'] = LLMain.current_octave
            print(f"Octave locked for note {note_id} at octave {note_info['locked_octave']}")
            # Reload sound with the locked octave
            LLAudio.preload_sound_for_looping_note(note_id, note_info['key'])
        else:
            print(f"Note {note_id} is already octave locked at octave {note_info['locked_octave']}")
    print("All octaves locked.")
    # Update the GUI display
    if LLMain.advanced_menu_window and LLMain.advanced_menu_window.winfo_exists():
        LLMain.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def unlock_all_octaves():
    """Unlock the octave for all looping notes."""
    for note_id, note_info in LLMain.looping_notes.items():
        note_info['octave_locked'] = False
        # Reload sounds with the current global octave
        LLAudio.preload_sound_for_looping_note(note_id, note_info['key'])
    print("All octaves unlocked.")
    # Update the GUI display
    if LLMain.advanced_menu_window and LLMain.advanced_menu_window.winfo_exists():
        LLMain.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')
