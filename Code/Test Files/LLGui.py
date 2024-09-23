import tkinter as tk
from tkinter import ttk
import LLMain
import LLAudio as audio

def octave_buttons():
    """Create octave switcher buttons."""
    tk.Label(main_frame, text="Octave Switcher").grid(row=0, column=0, sticky='nsw')
    octave_buttons_frame = tk.Frame(main_frame)
    octave_buttons_frame.grid(row=1, column=0, sticky='nsw')

    main_frame.grid_rowconfigure(1, weight=10)
    octave_buttons_frame.grid_rowconfigure(0, weight=1)

    for i, octave in enumerate(LLMain.octave_range):
        octave_button = tk.Button(
            octave_buttons_frame,
            text=f"Octave {octave}",
            command=lambda o=octave: audio.change_octave(o),
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
        command=audio.adjust_volume,
        resolution=.01,
        width=padding_y * 4,
        activebackground="blue",
        showvalue=0,
        repeatdelay=100
    )
    volume_slider.set(LLMain.volume)
    volume_slider.grid(row=1, column=1, sticky='ns')

def instrument_buttons():
    """Create instrument switcher buttons."""
    tk.Label(main_frame, text="Instrument Switcher").grid(row=0, column=2, sticky='nse')
    instrument_button_frame = tk.Frame(main_frame)
    instrument_button_frame.grid(row=1, column=2, sticky='nse')

    instrument_button_frame.grid_rowconfigure(0, weight=1)
    instrument_button_frame.grid_columnconfigure(0, weight=1)

    for i, instrument in enumerate(LLMain.instrument_folders):
        instrument_button = tk.Button(
            instrument_button_frame,
            text=f"{instrument}",
            width=20,
            command=lambda i=instrument: audio.choose_folder(i),
            activebackground="blue",
            activeforeground="white"
        )
        instrument_button.grid(row=i, column=0, pady=padding_y, sticky='nse')
        instrument_button_frame.grid_rowconfigure(i, weight=1)

def advanced_menu():
    """Create the advanced options menu."""
    menu = tk.Toplevel(root)
    menu.title("Advanced Options")
    menu.attributes('-fullscreen', True)

    # Store the reference to the advanced menu window
    LLMain.advanced_menu_window = menu

    # Create a frame inside the advanced menu for layout
    advanced_frame = tk.Frame(menu)
    advanced_frame.pack(expand=True, fill='both', padx=padding_x, pady=padding_y)

    # Divide the advanced frame into columns
    advanced_frame.grid_columnconfigure(0, weight=1)
    advanced_frame.grid_columnconfigure(1, weight=1)

    # Left side: Key selection and other controls
    controls_frame = tk.Frame(advanced_frame)
    controls_frame.grid(row=0, column=0, sticky='nsew')

    tk.Label(controls_frame, text="Select Key").pack(pady=padding_y)
    key_dropdown = ttk.Combobox(controls_frame, values=LLMain.keys, state="readonly")
    key_dropdown.set(LLMain.current_key)
    key_dropdown.bind(
        "<<ComboboxSelected>>",
        lambda e: audio.change_key(key_dropdown.get())
    )
    key_dropdown.pack(pady=padding_y)

    # Sustain option
    sustain_var = tk.BooleanVar(value=LLMain.sustain_option)

    def update_sustain():
        LLMain.sustain_option = sustain_var.get()
        if LLMain.running:
            audio.preload_sounds()

    sustain_check = tk.Checkbutton(
        controls_frame,
        text="Sustain",
        variable=sustain_var,
        command=update_sustain
    )
    sustain_check.pack(pady=padding_y)

    # Loop button
    def activate_loop_mode():
        LLMain.loop_mode = True

    loop_button = tk.Button(
        controls_frame,
        text="Loop Next Note",
        command=activate_loop_mode
    )
    loop_button.pack(pady=padding_y)

    # Right side: Looping notes display
    looping_frame = tk.Frame(advanced_frame)
    looping_frame.grid(row=0, column=1, sticky='nsew')

    tk.Label(looping_frame, text="Looping Notes Slots").pack(pady=padding_y)

    # Reset the slot frames list
    LLMain.looping_slot_frames = []

    for i in range(LLMain.max_loops):
        slot_frame = tk.Frame(looping_frame, relief='sunken', borderwidth=1)
        slot_frame.pack(fill='x', pady=padding_y/4)

        slot_label = tk.Label(slot_frame, text=f"Slot {i+1}: Available")
        slot_label.pack(side='left', padx=padding_x/2)

        # Store both frame and label for future updates
        LLMain.looping_slot_frames.append({'frame': slot_frame, 'label': slot_label})

    # Bind a custom event to update the display
    menu.bind('<<UpdateLoopingNotesDisplay>>', update_looping_notes_display)

    # Call update_looping_notes_display to initialize the display
    update_looping_notes_display()

    button_frame = tk.Frame(menu)
    button_frame.pack(side=tk.BOTTOM, pady=padding_y)

    tk.Button(
        button_frame,
        text="Exit",
        command=menu.destroy,
        width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    if LLMain.running:
        menu.bind("<KeyPress>", audio.key_press)
        menu.bind("<KeyRelease>", audio.key_release)

    # Handle the advanced menu closing
    def on_advanced_menu_close():
        LLMain.advanced_menu_window = None
        menu.destroy()

    menu.protocol("WM_DELETE_WINDOW", on_advanced_menu_close)

    # Ensure the window remains on top and modal
    menu.grab_set()
    root.wait_window(menu)

def looping_notes_display():
    """Create a display for looping note slots."""
    looping_frame = tk.Frame(main_frame)
    looping_frame.grid(row=0, column=3, rowspan=2, sticky='nsew', padx=padding_x, pady=padding_y)
    main_frame.grid_columnconfigure(3, weight=1)

    tk.Label(looping_frame, text="Looping Notes Slots").pack(pady=padding_y)

    # Create a frame for each slot
    LLMain.looping_slot_frames = []

    for i in range(LLMain.max_loops):
        slot_frame = tk.Frame(looping_frame, relief='sunken', borderwidth=1)
        slot_frame.pack(fill='x', pady=padding_y/4)

        slot_label = tk.Label(slot_frame, text=f"Slot {i+1}: Available")
        slot_label.pack(side='left', padx=padding_x/2)

        # Store both frame and label for future updates
        LLMain.looping_slot_frames.append({'frame': slot_frame, 'label': slot_label})
    
    # Bind the custom event
    root.bind('<<UpdateLoopingNotesDisplay>>', update_looping_notes_display)


def update_looping_notes_display(event=None):
    """Update the display of looping note slots."""
    if not hasattr(LLMain, 'looping_slot_frames'):
        return  # Advanced menu is not open

    for i, slot_info in enumerate(LLMain.looping_slot_frames):
        note_id = LLMain.looping_note_slots[i]
        slot_label = slot_info['label']
        if note_id is not None:
            slot_label.config(text=f"Slot {i+1}: {note_id}")
        else:
            slot_label.config(text=f"Slot {i+1}: Available")



def start_harp():
    """Start the harp application."""
    audio.start_harp()
    start_button.config(text="Stop", command=stop_harp)
    root.bind("<KeyPress>", audio.key_press)
    root.bind("<KeyRelease>", audio.key_release)

def stop_harp():
    """Stop the harp application."""
    audio.stop_harp()
    start_button.config(text="Start", command=start_harp)
    root.unbind("<KeyPress>")
    root.unbind("<KeyRelease>")

def main_menu():
    """Set up the main GUI layout."""
    global start_button
    global root
    root = tk.Tk()
    LLMain.root = root
    root.title("Laser Harp Main Menu")
    root.attributes('-fullscreen', True)

    global screen_width
    global screen_height
    global padding_x
    global padding_y
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    padding_x = int(screen_width * 0.02)
    padding_y = int(screen_height * 0.02)

    global main_frame
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
        command=root.quit,
        width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    root.mainloop()
