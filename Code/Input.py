import Audio
import Helpers
import Looping
import Main

# GPIO pin mappings to notes
KEY_PINS = Main.KEY_PINS  # Reuse pin mapping from Main

def handle_key_press(pin):
    """Handle GPIO-based key press."""
    note = KEY_PINS[pin]
    octave = Main.current_octave
    if pin == 26:  # Handle octave shifts if "C2" is used for this purpose
        octave += 1
    note_id = Audio.get_note_identifier(note, octave)

    if Main.loop_mode:
        Looping.handle_loop_mode(note_id, note)  # Handle loop mode logic
    else:
        handle_normal_key_press(note_id, note)  # Handle standard key press logic

def handle_key_release(pin):
    """Handle GPIO-based key release."""
    note = Main.KEY_PINS[pin]
    if note in Main.KEY_PINS:
        Main.key_status[note] = False  # Mark the key as released
        if Main.sustain_option:
            # Cancel any scheduled sustain playback
            if note in Main.scheduled_tasks:
                Main.root.after_cancel(Main.scheduled_tasks[note])
                del Main.scheduled_tasks[note]

            # Stop the sustain sound
            Audio.stop_sustain_sound(note)
        else:
            Audio.stop_note_immediately(note)  # Stop normal playback

def handle_normal_key_press(note_id, note):
    """Handle normal key press logic."""
    if note_id in Main.looping_notes:
        # Stop the looping note if already active
        Looping.stop_looping_note(note_id)
    else:
        if not Main.key_status.get(note, False):  # Avoid duplicate presses
            Main.key_status[note] = True
            if Main.sustain_option:
                # Play attack sound, then trigger sustain loop
                sounds = Main.sound_objects[note]
                sounds['attack'].play()
                attack_length = int(sounds['attack'].get_length() * 1000)
                Main.root.after(attack_length, lambda: Audio.play_sustain_sound(note))
            else:
                # Play the original sound once
                sounds = Main.sound_objects[note]
                sounds['original'].play()

def handle_shift(direction):
    """Handle octave shifts triggered by GPIO inputs."""
    if direction == 'left':
        new_octave = Main.current_octave - 1
        if new_octave in Main.octave_range:
            Audio.change_octave(new_octave)
            print(f"Octave decreased to {new_octave}")
        else:
            print("Cannot decrease octave further.")
    elif direction == 'right':
        new_octave = Main.current_octave + 1
        if new_octave in Main.octave_range:
            Audio.change_octave(new_octave)
            print(f"Octave increased to {new_octave}")
        else:
            print("Cannot increase octave further.")

def po_gpio_inputs():
    """Po GPIO inputs to detect state changes."""
    for pin, note in KEY_PINS.items():
        pin_state = Main.gpio_chip.read(pin)
        if pin_state == 1 and not Main.key_status.get(note, False):  # Key press detected
            handle_key_press(pin)
        elif pin_state == 0 and Main.key_status.get(note, False):  # Key release detected
            handle_key_release(pin)
