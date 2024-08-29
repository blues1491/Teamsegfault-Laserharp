import pygame
import tkinter as tk
from tkinter import *
import os

pygame.mixer.init()

base_folder = "../Sound Samples/"
current_folder = base_folder + "Harp/"
volume = .5
current_octave = 4  # Default octave
sound_objects = {}
running = False 
octave_range = [2, 3, 4, 5, 6]
instrument_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

key_to_note = {
    '`': "C" ,
    '1': "C#",
    '2': "D" ,
    '3': "D#",
    '4': "E" ,
    '5': "F" ,
    '6': "F#",
    '7': "G" ,
    '8': "G#",
    '9': "A" ,
    '0': "A#",
    '-': "B" ,
    '=': "C"
}

def preload_sounds():
    global sound_objects
    sound_objects = {}
    for key, note in key_to_note.items():
        if key == '=':  # Special case for top C
            sound_file = f"{note}{current_octave + 1}.wav"
        else:
            sound_file = f"{note}{current_octave}.wav"
        sound = pygame.mixer.Sound(current_folder + sound_file)
        sound.set_volume(volume)
        sound_objects[key] = sound

def monitor_keyboard(event):
    global current_octave

    # Check for shift keys and adjust the octave
    if event.keysym == 'Shift_R':
        if current_octave < max(octave_range):
            current_octave += 1
            preload_sounds()
    elif event.keysym == 'Shift_L':
        if current_octave > min(octave_range):
            current_octave -= 1
            preload_sounds()

    key = event.char
    if key in sound_objects:
        sound_objects[key].play()

def start_harp():
    global running
    running = True
    preload_sounds()

    start_button.config(text="Stop", command=stop_harp)
    root.bind("<KeyPress>", monitor_keyboard)

def stop_harp():
    global running
    running = False
    start_button.config(text="Start", command=start_harp)
    root.unbind("<KeyPress>")

def adjust_volume(value):
    global volume
    volume = float(value)
    for sound in sound_objects.values():
        sound.set_volume(volume)

def choose_folder(folder_name):
    global current_folder
    current_folder = base_folder + folder_name + "/"
    if running:
        preload_sounds()

def change_octave(value):
    global current_octave
    current_octave = int(value)
    if running:
        preload_sounds()

def open_main_menu():
    global start_button
    global root
    root = tk.Tk()
    root.title("Laser Harp Main Menu")
    root.attributes('-fullscreen', True)
    #root.configure(background='black')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    padding_x = int(screen_width * 0.02)
    padding_y = int(screen_height * 0.02)

    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill='both', padx=padding_x, pady=padding_y)
    #main_frame.configure(background='black')

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)
   

    tk.Label(main_frame, text="Octave Switcher").grid(row=0, column=0, sticky='nsw')
    octave_buttons_frame = tk.Frame(main_frame)
    octave_buttons_frame.grid(row=1, column=0, sticky='nsw')
    
    main_frame.grid_rowconfigure(1, weight=10)
    octave_buttons_frame.grid_rowconfigure(0, weight=1)
    
    octave_button_height = (screen_height - padding_y * 2) / (len(octave_range) * 1.3)
    octave_button_padding = int(octave_button_height * 0.25)
    
    for i, octave in enumerate(octave_range):
        octave_button = tk.Button(octave_buttons_frame, text=f"Octave {octave}", command=lambda o=octave: change_octave(o), width=20, activebackground="blue", activeforeground="white")
        octave_button.grid(row=i * 2, column=0, pady=(0, octave_button_padding), sticky='nsw')
        octave_buttons_frame.grid_rowconfigure(i * 2, weight=1)


    tk.Label(main_frame, text="Volume").grid(row=0, column=1, pady=padding_y)
    volume_slider = tk.Scale(main_frame, from_=1, to=0, orient='vertical', command=adjust_volume, resolution=.01, width=padding_y*4, activebackground="blue", showvalue=0, repeatdelay=100)
    volume_slider.set(volume)
    volume_slider.grid(row=1, column=1, sticky='ns')

    
    tk.Label(main_frame, text="Instrument Switcher").grid(row=0, column=2, sticky='nse')
    instrument_button_frame = tk.Frame(main_frame)
    instrument_button_frame.grid(row=1, column=2, sticky='nse')

    instrument_button_frame.grid_rowconfigure(0, weight=1)
    instrument_button_frame.grid_columnconfigure(0, weight=1)

    instrument_button_height = (screen_height - padding_y * 2) / (len(instrument_folders) * 1.3)
    instrument_button_padding = int(instrument_button_height * 0.25)

    for i, instrument in enumerate(instrument_folders):
        photo = PhotoImage(file = base_folder + instrument + "/Image.png") 
        instrument_button = tk.Button(instrument_button_frame, text=f"{instrument}", width=20, command=lambda i=instrument: choose_folder(i), activebackground="blue", activeforeground="white")
        instrument_button.grid(row=i, column=0, pady=(0, instrument_button_padding), sticky='nse')
        instrument_button_frame.grid_rowconfigure(i, weight=1)


    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=padding_y)

    start_button = tk.Button(button_frame, text="Start", command=start_harp)
    start_button.pack(side=tk.LEFT, padx=padding_x)
    
    tk.Button(button_frame, text="Exit", command=root.quit).pack(side=tk.RIGHT, padx=padding_x)

    root.mainloop()

if __name__ == "__main__":
    open_main_menu()
