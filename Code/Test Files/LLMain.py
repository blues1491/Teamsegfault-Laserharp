import pygame
import tkinter as tk
from tkinter import ttk
import os
from pydub import AudioSegment
from io import BytesIO
import LLAudio as audio
import LLGui as gui

pygame.mixer.init()

running = False

if __name__ == "__main__":
    gui.main_menu()
