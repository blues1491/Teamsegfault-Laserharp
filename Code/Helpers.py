# Helpers.py

import os
import Main

def transpose_note(note, key, octave, locked_key=None):
    """Transpose a note based on the current key or locked key, adjusting the octave if necessary."""
    used_key = locked_key if locked_key else key
    key_index = Main.keys.index(used_key)
    note_index = Main.keys.index(note)
    transposed_index = (note_index + key_index) % len(Main.keys)
    transposed_note = Main.keys[transposed_index]
    # If transposed_index < note_index, we've wrapped around, so increment the octave
    octave_adjustment = 0
    if transposed_index < note_index:
        octave_adjustment = 1
    return transposed_note, octave + octave_adjustment

def get_note_identifier(pin, octave, instrument=None):
    """Generate a unique identifier for a note based on its transposed note, octave, and instrument."""
    original_note = Main.KEY_PINS[pin]
    transposed_note, adjusted_octave = transpose_note(original_note, Main.current_key, octave)
    if pin == 5:
        adjusted_octave += 1
    instrument_part = f"_{os.path.basename(instrument)}" if instrument else ""
    return f"{transposed_note}{adjusted_octave}{instrument_part}"

def key_to_index(key):
    """Convert a musical key (e.g., 'C', 'D#') to its index in Main.keys."""
    if isinstance(key, int):
        return key  # Already an index
    if key in Main.keys:
        return Main.keys.index(key)
    raise ValueError(f"Invalid key: {key}")

def note_to_gpio(note):
    """Map a musical note (e.g., 'C', 'D#') to its GPIO pin."""
    for pin, note_name in Main.KEY_PINS.items():
        if note_name == note:
            return pin
    raise KeyError(f"Note '{note}' not found in GPIO mapping.")
