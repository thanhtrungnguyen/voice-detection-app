import customtkinter as ctk
import pygame

from src.frame.plot_frame import PlotFrame
from src.frame.sound_player_frame import SoundPlayer
from src.model.playing_sound import PlayingSound
from src.service.voice_activity_detector import VoiceActivityDetector

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
        self.voice_activity_detector = None
        self.title("Voice Activity Detection")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")

        self.playing_sound = PlayingSound()

        self.sound_player = SoundPlayer(self, self.playing_sound)

        # Create the PlotFrame as part of MainFrame but initially hidden
        self.plot_frame = PlotFrame(self, self.playing_sound)

        self.update_playing_info()
        # self.show_plot()

    def update_playing_info(self):
        # Initialize the VoiceActivityDetector when a new sound is played
        # if self.playing_sound.path and not self.voice_activity_detector:
        #     self.voice_activity_detector = VoiceActivityDetector(self.playing_sound)
        #     self.voice_activity_detector.plot_detected_speech_regions()

        self.after(100, self.update_playing_info)  # Update every second

    def show_plot(self):
        # Display the plot when a sound starts playing
        self.plot_frame.lift()
        self.plot_frame.display_plot()  # Call the method to generate and show the graph


