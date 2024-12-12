import os
import tkinter as tk
from tkinter import ttk
import Main
import Audio

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

def sustain_toggle():
    """Add a toggle for sustain."""
    tk.Label(main_frame, text="Sustain").grid(row=2, column=0, pady=padding_y)
    sustain_var = tk.BooleanVar(value=Main.sustain_option)

    def update_sustain():
        Main.sustain_option = sustain_var.get()

    sustain_check = tk.Checkbutton(
        main_frame,
        text="Enable Sustain",
        variable=sustain_var,
        command=update_sustain
    )
    sustain_check.grid(row=3, column=0, pady=padding_y, sticky='nsw')

def key_selector():
    """Add a dropdown for key selection."""
    tk.Label(main_frame, text="Key Selector").grid(row=2, column=2, pady=padding_y)
    key_dropdown = ttk.Combobox(main_frame, values=Main.keys, state="readonly")
    key_dropdown.set(Main.current_key)
    key_dropdown.bind(
        "<<ComboboxSelected>>",
        lambda e: Audio.change_key(key_dropdown.get())
    )
    key_dropdown.grid(row=3, column=2, pady=padding_y, sticky='nse')

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
    global start_button
    global root
    root = tk.Tk()
    Main.root = root
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
    sustain_toggle()
    key_selector()

    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=padding_y)

    start_button = tk.Button(button_frame, text="Start", command=start_harp, width=20)
    start_button.pack(side=tk.LEFT, padx=padding_x)

    tk.Button(
        button_frame,
        text="Exit",
        command=root.quit,
        width=20
    ).pack(side=tk.RIGHT, padx=padding_x)

    root.mainloop()
