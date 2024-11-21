import os
import tkinter as tk
from tkinter import ttk
import Audio
import Main
import Looping

# Constants for UI layout
padding_x = 20
padding_y = 10

def octave_buttons():
    """Create octave switcher buttons."""
    tk.Label(main_frame, text="Octave Switcher").grid(row=0, column=0, sticky='nsw')
    octave_buttons_frame = tk.Frame(main_frame)
    octave_buttons_frame.grid(row=1, column=0, sticky='nsw')

    for i, octave in enumerate(Main.octave_range):
        octave_button = tk.Button(
            octave_buttons_frame,
            text=f"Octave {octave}",
            command=lambda o=octave: Audio.change_octave(o),
            width=20,
            activebackground="blue",
            activeforeground="white"
        )
        octave_button.grid(row=i, column=0, pady=padding_y, sticky='nsw')

def volume_slider():
    """Create volume slider."""
    tk.Label(main_frame, text="Volume").grid(row=0, column=1, pady=padding_y)
    volume_slider = tk.Scale(
        main_frame,
        from_=1,
        to=0,
        orient='vertical',
        command=Audio.adjust_volume,
        resolution=.01,
        width=20,
        activebackground="blue",
        showvalue=0,
        repeatdelay=100
    )
    volume_slider.set(Main.volume)
    volume_slider.grid(row=1, column=1, sticky='ns')

def instrument_buttons():
    """Create instrument switcher buttons."""
    tk.Label(main_frame, text="Instrument Switcher").grid(row=0, column=2, sticky='nse')
    instrument_button_frame = tk.Frame(main_frame)
    instrument_button_frame.grid(row=1, column=2, sticky='nse')

    for i, instrument in enumerate(Main.instrument_folders):
        instrument_button = tk.Button(
            instrument_button_frame,
            text=f"{instrument}",
            width=20,
            command=lambda i=instrument: Audio.choose_folder(i),
            activebackground="blue",
            activeforeground="white"
        )
        instrument_button.grid(row=i, column=0, pady=padding_y, sticky='nse')

def advanced_menu():
    """Create the advanced options menu."""
    menu = tk.Toplevel(root)
    menu.title("Advanced Options")
    menu.attributes('-fullscreen', True)

    Main.advanced_menu_window = menu  # Reference for updates

    advanced_frame = tk.Frame(menu)
    advanced_frame.pack(expand=True, fill='both', padx=padding_x, pady=padding_y)

    advanced_frame.grid_columnconfigure(0, weight=1)
    advanced_frame.grid_columnconfigure(1, weight=1)

    # Controls for looping, sustain, etc.
    controls_frame = tk.Frame(advanced_frame)
    controls_frame.grid(row=0, column=0, sticky='nsew')

    tk.Label(controls_frame, text="Select Key").pack(pady=padding_y)
    key_dropdown = ttk.Combobox(controls_frame, values=Main.keys, state="readonly")
    key_dropdown.set(Main.current_key)
    key_dropdown.bind("<<ComboboxSelected>>", lambda e: Audio.change_key(key_dropdown.get()))
    key_dropdown.pack(pady=padding_y)

    sustain_var = tk.BooleanVar(value=Main.sustain_option)

    def update_sustain():
        Main.sustain_option = sustain_var.get()
        if Main.running:
            Audio.preload_sounds()

    sustain_check = tk.Checkbutton(
        controls_frame,
        text="Sustain",
        variable=sustain_var,
        command=update_sustain
    )
    sustain_check.pack(pady=padding_y)

    loop_button = tk.Button(
        controls_frame,
        text="Loop Next Note",
        command=lambda: setattr(Main, 'loop_mode', True)
    )
    loop_button.pack(pady=padding_y)

    stop_all_button = tk.Button(
        controls_frame,
        text="Stop All Loops",
        command=Looping.stop_all_loops
    )
    stop_all_button.pack(pady=padding_y)

    # Looping Notes Slots
    looping_frame = tk.Frame(advanced_frame)
    looping_frame.grid(row=0, column=1, sticky='nsew')

    tk.Label(looping_frame, text="Looping Notes Slots").pack(pady=padding_y)

    Main.looping_slot_frames = []  # Reset slot frames list

    for i in range(Main.max_loops):
        slot_frame = tk.Frame(looping_frame, relief='sunken', borderwidth=1)
        slot_frame.pack(fill='x', pady=padding_y / 4)

        slot_label = tk.Label(slot_frame, text=f"Slot {i + 1}: Available")
        slot_label.pack(side='left', padx=padding_x / 2)

        Main.looping_slot_frames.append({'frame': slot_frame, 'label': slot_label})

    # Add Lock/Unlock All Buttons
    lock_unlock_frame = tk.Frame(looping_frame)
    lock_unlock_frame.pack(pady=padding_y)

    tk.Button(
        lock_unlock_frame,
        text="Lock All Instruments",
        command=Looping.lock_all_instruments
    ).pack(side='left', padx=padding_x / 2)

    tk.Button(
        lock_unlock_frame,
        text="Unlock All Instruments",
        command=Looping.unlock_all_instruments
    ).pack(side='right', padx=padding_x / 2)

    tk.Button(
        lock_unlock_frame,
        text="Lock All Keys",
        command=Looping.lock_all_keys
    ).pack(side='left', padx=padding_x / 2)

    tk.Button(
        lock_unlock_frame,
        text="Unlock All Keys",
        command=Looping.unlock_all_keys
    ).pack(side='right', padx=padding_x / 2)

    menu.bind('<<UpdateLoopingNotesDisplay>>', update_looping_notes_display)

    button_frame = tk.Frame(menu)
    button_frame.pack(side=tk.BOTTOM, pady=padding_y)

    tk.Button(
        button_frame,
        text="Exit",
        command=menu.destroy,
        width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    menu.grab_set()
    root.wait_window(menu)

def update_looping_notes_display(event=None):
    """Update the display of looping note slots."""
    if not hasattr(Main, 'looping_slot_frames'):
        return

    for i, slot_info in enumerate(Main.looping_slot_frames):
        note_id = Main.looping_note_slots[i]
        slot_label = slot_info['label']
        if note_id is not None:
            note_info = Main.looping_notes[note_id]
            display_note = f"{note_info['key']} (Oct: {note_info['locked_octave'] if note_info['octave_locked'] else Main.current_octave})"
            slot_label.config(text=f"Slot {i + 1}: {display_note}")
        else:
            slot_label.config(text=f"Slot {i + 1}: Available")

def start_harp():
    """Start the harp application."""
    Audio.start_harp()
    start_button.config(text="Stop", command=stop_harp)

def stop_harp():
    """Stop the harp application."""
    Audio.stop_harp()
    start_button.config(text="Start", command=start_harp)

def main_menu():
    """Set up the main GUI layout."""
    global root, main_frame, start_button
    root = tk.Tk()
    Main.root = root
    root.title("Laser Harp Main Menu")
    root.attributes('-fullscreen', True)

    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill='both', padx=padding_x, pady=padding_y)

    octave_buttons()
    volume_slider()
    instrument_buttons()

    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=padding_y)

    start_button = tk.Button(button_frame, text="Start", command=start_harp, width=20)
    start_button.pack(side=tk.LEFT, padx=padding_x)

    tk.Button(
        button_frame,
        text="Advanced Options",
        command=advanced_menu,
        width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    tk.Button(
        button_frame,
        text="Exit",
        command=root.quit,
        width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    root.mainloop()
