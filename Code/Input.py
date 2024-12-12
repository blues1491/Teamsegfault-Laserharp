import Main
import Audio

def handle_gpio_input(pin):
    """Handle GPIO input events for note playback."""
    note = Main.gpio_to_note.get(pin)
    if note:
        if not Main.key_status.get(pin, False):  # Note is not already playing
            play_gpio_triggered_note(note, pin)
            Main.key_status[pin] = True

def release_gpio_input(pin):
    """Handle GPIO input release events for note stop."""
    note = Main.gpio_to_note.get(pin)
    if note and Main.key_status.get(pin, False):  # Note was playing
        stop_gpio_triggered_note(note)
        Main.key_status[pin] = False

def play_gpio_triggered_note(note, pin):
    """Play a note triggered by GPIO."""
    if Main.sustain_option:
        sounds = Main.sound_objects[note]
        sounds['attack'].play()
        attack_length = int(sounds['attack'].get_length() * 1000)
        Main.root.after(attack_length, lambda: Audio.schedule_sustain_play(note))
    else:
        sounds = Main.sound_objects[note]
        sounds['original'].play()

def stop_gpio_triggered_note(note):
    """Stop a note triggered by GPIO."""
    if Main.sustain_option:
        if note in Main.scheduled_tasks:
            Main.root.after_cancel(Main.scheduled_tasks[note])
            del Main.scheduled_tasks[note]
    # No action needed for immediate stop in non-sustain mode
