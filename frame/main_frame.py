import customtkinter as ctk
import pygame

from frame.plot_frame import PlotFrame
from frame.sound_player_frame import SoundPlayer
from model.playing_sound import PlayingSound

# Set the appearance and theme of the window
ctk.set_appearance_mode('Light')
ctk.set_default_color_theme("green")

# Window dimensions
APP_WIDTH, APP_HEIGHT = 1600, 900

# Initialize pygame mixer
pygame.mixer.init()


class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voice Activity Detection")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")

        self.playing_sound = PlayingSound()

        self.sound_player = SoundPlayer(self, self.playing_sound)
        self.plot_data = PlotFrame(self, self.playing_sound)

    def update_playing_info(self):
        # Update the label with the current sound path and progress
        self.current_playing_label.configure(
            text=f"Playing: {self.playing_sound.path} | Progress: {self.playing_sound.progress:.2f}s"
        )

        # Initialize the VoiceActivityDetector when a new sound is played
        # if self.playing_sound.path and not self.voice_activity_detector:
        #     self.voice_activity_detector = VoiceActivityDetector(self.playing_sound)
        #     self.voice_activity_detector.plot_detected_speech_regions()

        self.after(1000, self.update_playing_info)  # Update every second

