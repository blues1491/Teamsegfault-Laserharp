import os
import pygame
from pydub import AudioSegment
from io import BytesIO
import LLMain
import time

# Initialize the mixer with more channels if needed
pygame.mixer.set_num_channels(64)

# Helper Functions

def convert_pydub_to_pygame(sound):
    """Convert a pydub AudioSegment to a pygame Sound object."""
    raw_data = BytesIO()
    sound.export(raw_data, format="wav")
    raw_data.seek(0)
    return pygame.mixer.Sound(file=raw_data)

def transpose_note(note, key):
    """Transpose a note based on the current key."""
    key_index = LLMain.keys.index(key)
    note_index = LLMain.keys.index(note)
    transposed_index = (note_index + key_index) % len(LLMain.keys)
    transposed_note = LLMain.keys[transposed_index]

    octave_adjustment = 1 if transposed_index < key_index else 0
    return transposed_note, LLMain.current_octave + octave_adjustment

def get_note_identifier(key):
    """Generate a unique identifier for a note based on its transposed note and octave."""
    original_note = LLMain.input_to_note[key]
    transposed_note, octave = transpose_note(original_note, LLMain.current_key)
    if key == '=':
        octave += 1
    return f"{transposed_note}{octave}"

# Main Functions

def preload_sounds():
    """Preload all the sounds and process them for sustain and looping modes."""
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

        # Process sound for sustain and looping modes
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

        # Store sounds in the dictionary
        LLMain.sound_objects[input_key] = {
            'attack': attack_sound,
            'sustain': sustain_sound
        }

        # Store sustain sound length
        LLMain.sustain_lengths[input_key] = sustain_sound.get_length() * 1000  # in milliseconds

        # Also store the original sound for non-sustain playback
        original_sound = convert_pydub_to_pygame(sound)
        original_sound.set_volume(LLMain.volume)
        LLMain.sound_objects[input_key]['original'] = original_sound

def key_press(event):
    """Handle key press events."""
    keysym = event.keysym
    key = event.char
    current_time = time.time()

    if keysym == 'Shift_L':
        if current_time - LLMain.last_shift_l_time > LLMain.shift_cooldown:
            # Left shift pressed, decrease octave
            new_octave = LLMain.current_octave - 1
            if new_octave in LLMain.octave_range:
                change_octave(new_octave)
                LLMain.last_shift_l_time = current_time
                print(f"Octave decreased to {new_octave}")
            else:
                print("Cannot decrease octave further.")
    elif keysym == 'Shift_R':
        if current_time - LLMain.last_shift_r_time > LLMain.shift_cooldown:
            # Right shift pressed, increase octave
            new_octave = LLMain.current_octave + 1
            if new_octave in LLMain.octave_range:
                change_octave(new_octave)
                LLMain.last_shift_r_time = current_time
                print(f"Octave increased to {new_octave}")
            else:
                print("Cannot increase octave further.")
    elif key in LLMain.input_to_note:
        # Existing note handling code...

        note_id = get_note_identifier(key)
        if LLMain.loop_mode:
            # Handle looping
            if note_id in LLMain.looping_notes:
                # Note is already looping, stop looping it
                stop_looping_note(note_id)
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
        else:
            # Normal key press handling
            if not LLMain.key_status.get(key, False):
                LLMain.key_status[key] = True
                if note_id in LLMain.looping_notes:
                    pass  # Skip normal press if the note is already looping
                else:
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
            note_id = get_note_identifier(key)
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
        interval = int(sustain_length / LLMain.max_loops)

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
    note_id = get_note_identifier(key)
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

    sounds = LLMain.sound_objects[key]

    if LLMain.sustain_option:
        # Play the attack sound and schedule sustain playbacks
        sounds['attack'].play()
        attack_length = int(sounds['attack'].get_length() * 1000)
        task_id = LLMain.root.after(attack_length, lambda: schedule_loop_sustain_play(key, note_id))
        channel = pygame.mixer.find_channel()
        LLMain.looping_notes[note_id] = {'task_id': task_id, 'channel': channel, 'key': key, 'slot': slot_index}
        print(f"Started looping note with sustain: {note_id}")
    else:
        # Play the original sound back to back without sustain settings
        channel = pygame.mixer.find_channel()
        task_id = LLMain.root.after(0, lambda: schedule_normal_loop_play(key, note_id))
        LLMain.looping_notes[note_id] = {'task_id': task_id, 'channel': channel, 'key': key, 'slot': slot_index}
        print(f"Started looping note normally: {note_id}")

    # Update the looping note slot
    LLMain.looping_note_slots[slot_index] = note_id

     # Update the GUI display if advanced menu is open
    if LLMain.advanced_menu_window:
        LLMain.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

def schedule_normal_loop_play(key, note_id):
    """Schedule the next playback of the original sound for normal looping."""
    if note_id in LLMain.looping_notes:
        sounds = LLMain.sound_objects[key]
        channel = LLMain.looping_notes[note_id]['channel']
        channel.play(sounds['original'])
        sound_length = int(sounds['original'].get_length() * 1000)
        task_id = LLMain.root.after(sound_length, lambda: schedule_normal_loop_play(key, note_id))
        LLMain.looping_notes[note_id]['task_id'] = task_id
    else:
        # If the note is no longer looping, do nothing
        pass

def schedule_loop_sustain_play(key, note_id):
    """Schedule the sustain sound to play with overlaps for looping."""
    if note_id in LLMain.looping_notes:
        play_sustain_sound(key)
        # Calculate interval between sustain plays
        sustain_length = LLMain.sustain_lengths[key]
        interval = int(sustain_length / LLMain.max_overlaps)
        # Schedule the next sustain play
        task_id = LLMain.root.after(interval, lambda: schedule_loop_sustain_play(key, note_id))
        LLMain.looping_notes[note_id]['task_id'] = task_id
    else:
        # If note is no longer looping, do nothing
        pass

def stop_looping_note(note_id):
    """Stop looping a note and free its slot."""
    if note_id in LLMain.looping_notes:
        # Cancel scheduled tasks
        task_info = LLMain.looping_notes[note_id]
        task_id = task_info.get('task_id')
        channel = task_info.get('channel')
        slot_index = task_info.get('slot')

        if task_id:
            LLMain.root.after_cancel(task_id)

        if channel:
            if LLMain.sustain_option:
                # Apply fade out if sustain is on
                if LLMain.fade_out_duration > 0:
                    channel.fadeout(LLMain.fade_out_duration)
                else:
                    channel.stop()
            else:
                # Stop immediately if sustain is off
                channel.stop()

        # Remove looping note
        del LLMain.looping_notes[note_id]

        # Free the slot
        LLMain.looping_note_slots[slot_index] = None

        # Update the GUI display
        if LLMain.advanced_menu_window:
            LLMain.advanced_menu_window.event_generate('<<UpdateLoopingNotesDisplay>>', when='tail')

        print(f"Stopped looping note: {note_id}")
    else:
        print(f"Note {note_id} is not currently looping.")


def start_harp():
    """Initialize and start the harp application."""
    LLMain.running = True
    preload_sounds()

def stop_harp():
    """Stop the harp application and clean up."""
    LLMain.running = False
    pygame.mixer.stop()
    # Stop all looping notes and cancel scheduled tasks
    for note_id in list(LLMain.looping_notes.keys()):
        stop_looping_note(note_id)
    # Cancel any scheduled sustain plays
    for key in list(LLMain.scheduled_tasks.keys()):
        LLMain.root.after_cancel(LLMain.scheduled_tasks[key])
    LLMain.scheduled_tasks.clear()

def adjust_volume(value):
    """Adjust the volume of all sounds."""
    LLMain.volume = float(value)
    for sounds in LLMain.sound_objects.values():
        sounds['attack'].set_volume(LLMain.volume)
        sounds['sustain'].set_volume(LLMain.volume)
        sounds['original'].set_volume(LLMain.volume)

# Change settings functions

def change_octave(octave):
    """Change the current octave."""
    LLMain.current_octave = int(octave)
    if LLMain.running:
        preload_sounds()

def choose_folder(folder_name):
    """Change the current instrument folder."""
    LLMain.current_folder = LLMain.base_folder + folder_name + "/"
    if LLMain.running:
        preload_sounds()

def change_key(key):
    """Change the current key."""
    LLMain.current_key = key
    if LLMain.running:
        preload_sounds()
