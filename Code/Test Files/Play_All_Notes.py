import os
import time
import pygame

pygame.mixer.init()

base_folder = "../Sound Samples/"
instruments = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

note_order = [
    "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
    "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
    "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
    "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
    "C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6"
]

for instrument in instruments:
    audio_directory = base_folder + instrument + "/"
    
    for note in note_order:
        file_path = os.path.join(audio_directory, f"{note}.wav")
        
        if os.path.isfile(file_path):
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                print(f"{instrument} {note}")
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
            except Exception as e:
                print(f"Error playing {instrument} {note}: {e}")
        else:
            print(f"Note {instrument} {note} not found in the directory.")
        
    print(f"Finished playing all {instrument} notes")
    
print("Finished playing all available notes.")
