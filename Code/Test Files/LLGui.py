import tkinter as tk
from tkinter import ttk
import LLMain
import LLAudio as audio

# GUI for Octave buttons
def octave_buttons():
    tk.Label(main_frame, text="Octave Switcher").grid(row=0, column=0, sticky='nsw')
    octave_buttons_frame = tk.Frame(main_frame)
    octave_buttons_frame.grid(row=1, column=0, sticky='nsw')
    
    main_frame.grid_rowconfigure(1, weight=10)
    octave_buttons_frame.grid_rowconfigure(0, weight=1)
    
    octave_button_height = (screen_height - padding_y * 2) / (len(LLMain.octave_range) * 1.3)
    octave_button_padding = int(octave_button_height * 0.25)
    
    for i, octave in enumerate(LLMain.octave_range):
        octave_button = tk.Button(octave_buttons_frame, text=f"Octave {octave}", command=lambda o=octave: audio.change_octave(o), width=20, activebackground="blue", activeforeground="white")
        octave_button.grid(row=i * 2, column=0, pady=(0, octave_button_padding), sticky='nsw')
        octave_buttons_frame.grid_rowconfigure(i * 2, weight=1)

# GUI for Volume slider
def volume_slider():
    tk.Label(main_frame, text="Volume").grid(row=0, column=1, pady=padding_y)
    volume_slider = tk.Scale(main_frame, from_=1, to=0, orient='vertical', command=audio.adjust_volume, resolution=.01, width=padding_y*4, activebackground="blue", showvalue=0, repeatdelay=100)
    volume_slider.set(LLMain.volume)
    volume_slider.grid(row=1, column=1, sticky='ns')

# GUI for Instrument buttons
def instrument_buttons():
    tk.Label(main_frame, text="Instrument Switcher").grid(row=0, column=2, sticky='nse')
    instrument_button_frame = tk.Frame(main_frame)
    instrument_button_frame.grid(row=1, column=2, sticky='nse')

    instrument_button_frame.grid_rowconfigure(0, weight=1)
    instrument_button_frame.grid_columnconfigure(0, weight=1)

    instrument_button_height = (screen_height - padding_y * 2) / (len(LLMain.instrument_folders) * 1.3)
    instrument_button_padding = int(instrument_button_height * 0.25)

    for i, instrument in enumerate(LLMain.instrument_folders):
        instrument_button = tk.Button(instrument_button_frame, text=f"{instrument}", width=20, command=lambda i=instrument: audio.choose_folder(i), activebackground="blue", activeforeground="white")
        instrument_button.grid(row=i, column=0, pady=(0, instrument_button_padding), sticky='nse')
        instrument_button_frame.grid_rowconfigure(i, weight=1)

# Advanced settings menu
def advanced_menu():
    menu = tk.Toplevel(root)
    menu.title("Advanced Options")
    menu.attributes('-fullscreen', True)
    
    tk.Label(menu, text="Select Key").pack(pady=padding_y)
    key_dropdown = ttk.Combobox(menu, values=LLMain.keys, state="readonly")
    key_dropdown.set(LLMain.current_key)
    key_dropdown.bind("<<ComboboxSelected>>", lambda e: audio.change_key(key_dropdown.get()))
    key_dropdown.pack(pady=padding_y)

    # Add sustain option
    sustain_var = tk.BooleanVar(value=LLMain.sustain_option)

    def update_sustain():
        LLMain.sustain_option = sustain_var.get()
        if LLMain.running:
            audio.preload_sounds()
        print(f"Sustain option updated to: {LLMain.sustain_option}")

    sustain_check = tk.Checkbutton(menu, text="Sustain", variable=sustain_var, command=update_sustain)
    sustain_check.pack(pady=padding_y)

    button_frame = tk.Frame(menu)
    button_frame.pack(side=tk.BOTTOM, pady=padding_y)

    tk.Button(button_frame, text="Exit", command=menu.destroy, width=20).pack(side=tk.RIGHT, padx=padding_x)
    
    if LLMain.running:
        menu.bind("<KeyPress>", audio.key_press)
        menu.bind("<KeyRelease>", audio.key_release)
    
    # Ensure the window remains on top and modal
    menu.grab_set()
    root.wait_window(menu)
           
# Functions to start and stop harp
def start_harp():
    audio.start_harp()
    start_button.config(text="Stop", command=stop_harp)
    root.bind("<KeyPress>", audio.key_press)
    root.bind("<KeyRelease>", audio.key_release)

def stop_harp():
    audio.stop_harp()
    start_button.config(text="Start", command=start_harp)
    root.unbind("<KeyPress>")
    root.unbind("<KeyRelease>")

# Main GUI layout
def main_menu():
    global start_button
    global root
    root = tk.Tk()
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
    
    tk.Button(button_frame, text="Advanced Options", command=advanced_menu, width=20).pack(side=tk.RIGHT, padx=padding_x)

    tk.Button(button_frame, text="Exit", command=root.quit, width=20).pack(side=tk.RIGHT, padx=padding_x)

    root.mainloop()
