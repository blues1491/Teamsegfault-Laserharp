import os
import sys
import tkinter as tk
from tkinter import ttk
import Audio
import Helpers
import Main
import Looping

# Constants for UI layout
padding_x = 0
padding_y = 0

def octave_buttons():
    """Create octave switcher buttons."""
    tk.Label(main_frame, text="Octave Switcher").grid(row=0, column=0, sticky='nsw')
    octave_buttons_frame = tk.Frame(main_frame)
    octave_buttons_frame.grid(row=1, column=0, sticky='nsw')

    main_frame.grid_rowconfigure(1, weight=10)
    octave_buttons_frame.grid_rowconfigure(0, weight=1)

    for i, octave in enumerate(Main.octave_range):
        octave_button = tk.Button(
            octave_buttons_frame,
            text=f"Octave {octave}",
            command=lambda o=octave: Audio.change_octave(o),
            width=20,
            activebackground="blue",
            activeforeground="white"
        )
        octave_button.grid(row=i * 2, column=0, pady=padding_y, sticky='nsw')
        octave_buttons_frame.grid_rowconfigure(i * 2, weight=1)

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
        width=padding_y * 4,
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

    instrument_button_frame.grid_rowconfigure(0, weight=1)
    instrument_button_frame.grid_columnconfigure(0, weight=1)

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
        instrument_button_frame.grid_rowconfigure(i, weight=1)

def advanced_menu():
    """Create the advanced options menu."""
    menu = tk.Toplevel(Main.root)
    menu.title("Advanced Options")
    menu.attributes('-fullscreen', True)

    Main.advanced_menu_window = menu  # Reference for updates

    advanced_frame = tk.Frame(menu)
    advanced_frame.grid(row=0, column=0, sticky='nsew')

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

    # Unlock All Buttons
    unlock_all_frame = tk.Frame(advanced_frame)
    unlock_all_frame.grid(row=1, column=0, columnspan=2, pady=padding_y)

    # Looping Notes Slots
    Main.looping_notes_frame = tk.Frame(advanced_frame)
    Main.looping_notes_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')

    tk.Label(Main.looping_notes_frame, text="Looping Notes Slots").pack(pady=padding_y)

    Main.looping_slot_frames = []  # Reset slot frames list

    for i in range(Main.max_loops):
        slot_frame = tk.Frame(Main.looping_notes_frame, relief='sunken', borderwidth=1)
        slot_frame.pack(fill='x', pady=padding_y / 4)

        slot_label = tk.Label(slot_frame, text=f"Slot {i + 1}: Available")
        slot_label.pack(side='left', padx=padding_x / 2)

        Main.looping_slot_frames.append({'frame': slot_frame, 'label': slot_label})

    menu.bind('<<UpdateLoopingNotesDisplay>>', update_looping_notes_display)

    update_looping_notes_display()

    button_frame = tk.Frame(menu)
    button_frame.grid(row=3, column=0, columnspan=2, pady=padding_y)

    tk.Button(
        button_frame,
        text="Exit",
        command=menu.destroy,
        width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    menu.grab_set()
    Main.root.wait_window(menu)

def update_looping_notes_display(event=None):
    """Update the display of looping notes in the advanced menu."""
    if Main.advanced_menu_window and Main.advanced_menu_window.winfo_exists():
        # Clear existing widgets in the looping notes frame
        for widget in Main.looping_notes_frame.winfo_children():
            widget.destroy()

        # Repopulate the looping notes slots
        for i, note_id in enumerate(Main.looping_note_slots):
            slot_frame = tk.Frame(Main.looping_notes_frame, relief='sunken', borderwidth=1)
            slot_frame.pack(fill='x', pady=5)

            if note_id is not None:
                note_info = Main.looping_notes[note_id]

                # Display note details
                tk.Label(slot_frame, text=f"Slot {i + 1}").pack(side='left', padx=10)
                tk.Label(slot_frame, text=f"Instrument: {os.path.basename(note_info['locked_instrument'])}").pack(side='left', padx=10)

                tk.Button(
                    slot_frame,
                    text="Unlock Key and octave",
                    command=lambda note_id=note_id: Looping.unlock_key_and_octave(note_id)
                ).pack(side='right', padx=5)

                tk.Button(
                    slot_frame,
                    text="Stop",
                    command=lambda note_id=note_id: Looping.stop_looping(note_id)
                ).pack(side='right', padx=5)

            else:
                # Show available slot
                tk.Label(slot_frame, text=f"Slot {i + 1}: Available").pack(side='left', padx=10)

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
    Main.root.attributes('-fullscreen', True)
    Main.root.geometry(f"{Main.root.winfo_screenwidth()}x{Main.root.winfo_screenheight()}")
    Main.root.bind("<Escape>", lambda e: Main.root.attributes("-fullscreen", False))  # Exit fullscreen with Escape


    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    global padding_x 
    padding_x = int(screen_width * 0.02)
    global padding_y 
    padding_y = int(screen_height * 0.02)

    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill='both', padx=padding_x, pady=padding_y)

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)

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
    command=lambda: exit_program(),
    width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    def exit_program():
        """Cleanly exit the program."""
        try:
            Main.cleanup_gpio()  # Ensure GPIO pins are released
        except Exception as e:
            print(f"Error during cleanup: {e}")
        root.destroy()  # Close the GUI
        sys.exit()  # Terminate the program

    root.mainloop()
