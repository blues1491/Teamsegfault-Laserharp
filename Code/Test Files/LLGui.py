# LLGui.py

import tkinter
from tkinter import ttk

import pygame
import LLMain
import LLAudio
import LLLooping
import LLInput

def octave_buttons():
    """Create octave switcher buttons."""
    tkinter.Label(main_frame, text="Octave Switcher").grid(row=0, column=0, sticky='nsw')
    octave_buttons_frame = tkinter.Frame(main_frame)
    octave_buttons_frame.grid(row=1, column=0, sticky='nsw')

    main_frame.grid_rowconfigure(1, weight=10)
    octave_buttons_frame.grid_rowconfigure(0, weight=1)

    for i, octave in enumerate(LLMain.octave_range):
        octave_button = tkinter.Button(octave_buttons_frame, text=f"Octave {octave}", command=lambda o=octave: LLAudio.change_octave(o), width=padding_x, activebackground="blue", activeforeground="white")
        octave_button.grid(row=i * 2, column=0, pady=padding_y, sticky='nsw')
        octave_buttons_frame.grid_rowconfigure(i * 2, weight=1)

def volume_slider():
    """Create volume slider."""
    tkinter.Label(main_frame, text="Volume").grid(row=0, column=1, pady=padding_y)
    volume_slider = tkinter.Scale(
        main_frame,
        from_=1,
        to=0,
        orient='vertical',
        command=LLAudio.adjust_volume,
        resolution=.01,
        width=padding_x*2.5,
        activebackground="blue",
        showvalue=0,
        repeatdelay=100
    )
    volume_slider.set(LLMain.volume)
    volume_slider.grid(row=1, column=1, sticky='ns')

def instrument_buttons():
    """Create instrument switcher buttons."""
    tkinter.Label(main_frame, text="Instrument Switcher").grid(row=0, column=2, sticky='nse')
    instrument_button_frame = tkinter.Frame(main_frame)
    instrument_button_frame.grid(row=1, column=2, sticky='nse')

    instrument_button_frame.grid_rowconfigure(0, weight=1)
    instrument_button_frame.grid_columnconfigure(0, weight=1)

    for i, instrument in enumerate(LLMain.instrument_folders):
        instrument_button = tkinter.Button(instrument_button_frame, text=f"{instrument}", width=padding_x, command=lambda i=instrument: LLAudio.choose_folder(i), activebackground="blue", activeforeground="white")
        instrument_button.grid(row=i, column=0, pady=padding_y, sticky='nse')
        instrument_button_frame.grid_rowconfigure(i, weight=1)

def advanced_menu():
    """Create the advanced options menu."""
    menu = tkinter.Toplevel(root)
    menu.title("Advanced Options")
    menu.attributes('-fullscreen', True)

    # Store the reference to the advanced menu window
    LLMain.advanced_menu_window = menu

    # Create a frame inside the advanced menu for layout
    advanced_frame = tkinter.Frame(menu)
    advanced_frame.pack(expand=True, fill='both', padx=padding_x, pady=padding_y)

    # Divide the advanced frame into columns
    advanced_frame.grid_columnconfigure(0, weight=1)
    advanced_frame.grid_columnconfigure(1, weight=1)

    # Left side: Key selection and other controls
    controls_frame = tkinter.Frame(advanced_frame)
    controls_frame.grid(row=0, column=0, sticky='nsw')

    tkinter.Label(controls_frame, text="Select Key").pack(pady=padding_y)
    key_dropdown = ttk.Combobox(controls_frame, values=LLMain.keys, state="readonly", width=padding_x, height=12)
    key_dropdown.set(LLMain.current_key)
    key_dropdown.bind("<<ComboboxSelected>>", lambda e: LLAudio.change_key(key_dropdown.get()))
    key_dropdown.pack(pady=padding_y)

    # Sustain option
    sustain_var = tkinter.BooleanVar(value=LLMain.sustain_option)

    def update_sustain():
        LLMain.sustain_option = sustain_var.get()
        if LLMain.running:
            LLAudio.preload_sounds()

    sustain_check = tkinter.Checkbutton(controls_frame, text="Sustain", variable=sustain_var, command=update_sustain)
    sustain_check.pack(pady=padding_y)

    # Loop button
    def activate_loop_mode():
        LLMain.loop_mode = True

    loop_button = tkinter.Button(controls_frame, text="Loop Next Note", command=activate_loop_mode, width=padding_x, height=int(padding_y*.3))
    loop_button.pack(pady=padding_y)

    # Stop All Loops button
    stop_all_button = tkinter.Button(controls_frame, text="Stop All Loops", command=LLLooping.stop_all_loops, width=padding_x, height=int(padding_y*.3))
    stop_all_button.pack(pady=padding_y)

    # Right side: Looping notes display
    looping_frame = tkinter.Frame(advanced_frame)
    looping_frame.grid(row=0, column=1, sticky='nse')

    tkinter.Label(looping_frame, text="Looping Notes Slots").pack(pady=padding_y)

    # Reset the slot frames list
    LLMain.looping_slot_frames = []

    for i in range(LLMain.max_loops):
        slot_frame = tkinter.Frame(looping_frame, relief='sunken', borderwidth=1)
        slot_frame.pack(fill='x', pady=padding_y/4)

        slot_label = tkinter.Label(slot_frame, text=f"Slot {i+1}: Available", height=int(padding_y*.12))
        slot_label.pack(side='left', padx=padding_x/2)

        # Key lock checkbox
        key_lock_var = tkinter.BooleanVar()
        key_lock_check = tkinter.Checkbutton(slot_frame, text="Key Lock", variable=key_lock_var, command=lambda idx=i: LLLooping.toggle_key_lock(idx))
        key_lock_check.pack(side='right', padx=padding_x/2)

        # Octave lock checkbox
        octave_lock_var = tkinter.BooleanVar()
        octave_lock_check = tkinter.Checkbutton(slot_frame, text="Octave Lock", variable=octave_lock_var, command=lambda idx=i: LLLooping.toggle_octave_lock(idx))
        octave_lock_check.pack(side='right', padx=padding_x/2)

        # Stop Loop Button
        stop_loop_button = tkinter.Button(slot_frame, text="Stop", command=lambda idx=i: LLLooping.stop_loop_by_slot(idx), width=int(padding_x*.25), height=int(padding_y*.1))
        stop_loop_button.pack(side='right', padx=padding_x/2)

        # Store frame, label, and variables
        LLMain.looping_slot_frames.append({
            'frame': slot_frame,
            'label': slot_label,
            'octave_lock_var': octave_lock_var,
            'key_lock_var': key_lock_var  # Store the key lock variable
        })

    # Add Lock All and Unlock All buttons for octaves
    octave_lock_buttons_frame = tkinter.Frame(looping_frame)
    octave_lock_buttons_frame.pack(pady=padding_y)

    lock_all_octaves_button = tkinter.Button(octave_lock_buttons_frame, text="Lock All Octaves", command=LLLooping.lock_all_octaves, width=padding_x, height=int(padding_y*.17))
    lock_all_octaves_button.pack(side='left', padx=padding_x/2)

    unlock_all_octaves_button = tkinter.Button(octave_lock_buttons_frame, text="Unlock All Octaves", command=LLLooping.unlock_all_octaves, width=padding_x, height=int(padding_y*.17))
    unlock_all_octaves_button.pack(side='right', padx=padding_x/2)

    # Add Lock All and Unlock All buttons for keys
    key_lock_buttons_frame = tkinter.Frame(looping_frame)
    key_lock_buttons_frame.pack(pady=padding_y)

    lock_all_keys_button = tkinter.Button(key_lock_buttons_frame, text="Lock All Keys", command=LLLooping.lock_all_keys, width=padding_x, height=int(padding_y*.17))
    lock_all_keys_button.pack(side='left', padx=padding_x/2)

    unlock_all_keys_button = tkinter.Button(key_lock_buttons_frame, text="Unlock All Keys", command=LLLooping.unlock_all_keys, width=padding_x, height=int(padding_y*.17))
    unlock_all_keys_button.pack(side='right', padx=padding_x/2)

    # Bind a custom event to update the display
    menu.bind('<<UpdateLoopingNotesDisplay>>', update_looping_notes_display)

    # Call update_looping_notes_display to initialize the display
    update_looping_notes_display()

    button_frame = tkinter.Frame(menu)
    button_frame.pack(side=tkinter.BOTTOM, pady=padding_y)

    tkinter.Button(button_frame, text="Exit", command=menu.destroy, width=padding_x, height=int(padding_y*.2)).pack(side=tkinter.RIGHT, padx=padding_x)

    if LLMain.running:
        menu.bind("<KeyPress>", LLInput.key_press)
        menu.bind("<KeyRelease>", LLInput.key_release)

    # Handle the advanced menu closing
    def on_advanced_menu_close():
        LLMain.advanced_menu_window = None
        menu.destroy()

    menu.protocol("WM_DELETE_WINDOW", on_advanced_menu_close)

    # Ensure the window remains on top and modal
    menu.grab_set()
    root.wait_window(menu)

def update_looping_notes_display(event=None):
    """Update the display of looping note slots."""
    if not hasattr(LLMain, 'looping_slot_frames'):
        return  # Advanced menu is not open

    for i, slot_info in enumerate(LLMain.looping_slot_frames):
        note_id = LLMain.looping_note_slots[i]
        slot_label = slot_info['label']
        octave_lock_var = slot_info['octave_lock_var']
        key_lock_var = slot_info['key_lock_var']
        if note_id is not None:
            note_info = LLMain.looping_notes[note_id]
            key = note_info['key']
            original_note = LLMain.input_to_note[key]
            # Determine the correct octave
            if note_info['octave_locked']:
                octave = note_info['locked_octave']
            else:
                octave = LLMain.current_octave
            if key == '=':
                octave += 1
            # Use locked key if key is locked
            used_key = note_info['locked_key'] if note_info['key_locked'] else LLMain.current_key
            # Transpose the note based on the used key
            transposed_note, adjusted_octave = LLAudio.transpose_note(original_note, used_key, octave)
            display_note_id = f"{transposed_note}{adjusted_octave}"
            # Check if sustain mode is on for this looping note
            sustain_status = "Sustain" if note_info['sustain_option'] else "Normal"
            # Display key lock status
            key_status = f"Key Locked ({used_key})" if note_info['key_locked'] else "Key Unlocked"
            # Display octave lock status
            octave_status = f"Octave Locked ({octave})" if note_info['octave_locked'] else "Octave Unlocked"
            slot_label.config(text=f"Slot {i+1}: {display_note_id} ({sustain_status}, {key_status}, {octave_status})")
            # Update octave and key lock checkboxes
            octave_lock_var.set(note_info['octave_locked'])
            key_lock_var.set(note_info['key_locked'])
        else:
            slot_label.config(text=f"Slot {i+1}: Available")
            octave_lock_var.set(False)
            key_lock_var.set(False)

def start_harp():
    """Start the harp application."""
    LLMain.running = True
    LLAudio.preload_sounds()
    start_button.config(text="Stop", command=stop_harp)
    root.bind("<KeyPress>", LLInput.key_press)
    root.bind("<KeyRelease>", LLInput.key_release)

def stop_harp():
    """Stop the harp application."""
    LLMain.running = False
    pygame.mixer.stop()
    
    # Stop all looping notes and cancel scheduled tasks
    for note_id in list(LLMain.looping_notes.keys()):
        LLLooping.stop_looping_note(note_id)
        
    # Cancel any scheduled sustain plays
    for key in list(LLMain.scheduled_tasks.keys()):
        LLMain.root.after_cancel(LLMain.scheduled_tasks[key])
        
    LLMain.scheduled_tasks.clear()
    start_button.config(text="Start", command=start_harp)
    root.unbind("<KeyPress>")
    root.unbind("<KeyRelease>")

def main_menu():
    """Set up the main GUI layout."""
    global start_button
    global root
    root = tkinter.Tk()
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
    main_frame = tkinter.Frame(root)
    main_frame.pack(expand=True, fill='both', padx=padding_x, pady=padding_y)

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)

    octave_buttons()
    volume_slider()
    instrument_buttons()

    button_frame = tkinter.Frame(root)
    button_frame.pack(side=tkinter.BOTTOM, pady=padding_y)

    start_button = tkinter.Button(button_frame, text="Start", command=start_harp, width=padding_x, height=int(padding_y*.2))
    start_button.pack(side=tkinter.LEFT, padx=padding_x)

    tkinter.Button(button_frame, text="Advanced Options", command=advanced_menu, width=padding_x, height=int(padding_y*.2)).pack(side=tkinter.RIGHT, padx=padding_x)

    tkinter.Button(button_frame, text="Exit", command=root.quit, width=padding_x, height=int(padding_y*.2)).pack(side=tkinter.RIGHT, padx=padding_x)

    root.mainloop()
