import os
import time
import threading
import pygame
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
from mutagen.mp3 import MP3
import customtkinter as ctk

from src.model.playing_sound import PlayingSound


class SoundPlayer(ctk.CTkFrame):
    def __init__(self, parent, playing_sound: PlayingSound):
        super().__init__(parent)
        self.place(x=0, y=0, relwidth=0.3, relheight=1)

        # State variables
        self.current_position = 0
        self.paused = False
        self.selected_folder_path = ""
        self.playing_sound = playing_sound

        # UI components
        self.listbox = None
        self.progressbar = None
        self.create_widgets()

        # Start thread for progress bar update
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()

    def create_widgets(self):
        # Create and configure the listbox
        self.listbox = tk.Listbox(self, font=("TkDefaultFont", 16))

        # Create and configure the progressbar
        self.progressbar = Progressbar(self, length=300, mode="determinate")

        # Create buttons
        btn_select_folder = ctk.CTkButton(self, text="Select Sounds Folder", command=self.select_sounds_folder,
                                          font=("TkDefaultFont", 18))
        btn_previous = ctk.CTkButton(self, text="Previous", command=self.previous_sound, font=("TkDefaultFont", 18))
        btn_play = ctk.CTkButton(self, text="Play", command=self.play_sounds, font=("TkDefaultFont", 18))
        btn_pause = ctk.CTkButton(self, text="Pause", command=self.pause_sound, font=("TkDefaultFont", 18))
        btn_next = ctk.CTkButton(self, text="Next", command=self.next_sound, font=("TkDefaultFont", 18))

        # Layout configuration
        self.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1, uniform='a')

        # Place buttons in grid
        self.listbox.grid(row=0, column=0, rowspan=3, columnspan=4, sticky='nsew', padx=5, pady=5)
        btn_select_folder.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.progressbar.grid(row=5, column=0, columnspan=4, sticky='ew', padx=5, pady=5)

        btn_previous.grid(row=6, column=0)
        btn_play.grid(row=6, column=1)
        btn_pause.grid(row=6, column=2)
        btn_next.grid(row=6, column=3)

    def select_sounds_folder(self):
        self.selected_folder_path = filedialog.askdirectory()
        if self.selected_folder_path:
            self.listbox.delete(0, tk.END)
            for filename in os.listdir(self.selected_folder_path):
                if filename.endswith((".mp3", ".wav")):
                    self.listbox.insert(tk.END, filename)

    def previous_sound(self):
        current_index = self.listbox.curselection()
        if current_index and current_index[0] > 0:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(current_index[0] - 1)
            self.play_selected_sound()

    def next_sound(self):
        current_index = self.listbox.curselection()
        if current_index and current_index[0] < self.listbox.size() - 1:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(current_index[0] + 1)
            self.play_selected_sound()

    def play_sounds(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            self.play_selected_sound()

    def play_selected_sound(self):
        if self.listbox.curselection():
            current_index = self.listbox.curselection()[0]
            selected_sound = self.listbox.get(current_index)
            full_path = os.path.join(self.selected_folder_path, selected_sound)

            # Update the PlayingSound object with the current file path
            self.playing_sound.path = selected_sound
            self.playing_sound.progress = 0  # Reset progress

            self.load_and_play_sound(full_path)

    def load_and_play_sound(self, filepath):
        file_extension = os.path.splitext(filepath)[1].lower()

        # Load and play .wav or .mp3 files
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play(start=self.current_position)
        self.paused = False

        if file_extension == ".wav":
            # Use pygame to get the sound duration for .wav files
            sound = pygame.mixer.Sound(filepath)
            sound_duration = sound.get_length()
        elif file_extension == ".mp3":
            # Handle mp3 with mutagen for duration
            audio = MP3(filepath)
            sound_duration = audio.info.length
        else:
            return  # Unsupported file format

        self.progressbar["maximum"] = sound_duration

    def pause_sound(self):
        pygame.mixer.music.pause()
        self.paused = True

    def stop_sound(self):
        pygame.mixer.music.stop()
        self.paused = False
        self.progressbar["value"] = 0

    def update_progress(self):
        while True:
            if pygame.mixer.music.get_busy() and not self.paused:
                self.current_position = pygame.mixer.music.get_pos() / 1000
                self.progressbar["value"] = self.current_position

                # Update the PlayingSound object with the current progress
                self.playing_sound.progress = self.current_position

                # Stop playback when sound reaches the end
                if self.current_position >= self.progressbar["maximum"]:
                    self.stop_sound()

                self.update()
            time.sleep(0.1)
