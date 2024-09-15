import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.model.playing_sound import PlayingSound
from src.service.voice_activity_detector import VoiceActivityDetector


class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, playing_sound):
        super().__init__(parent)
        self.place(relx=0.3, y=0, relwidth=0.7, relheight=1)

        # Store the PlayingSound object
        self.playing_sound = playing_sound

        # Create label for displaying the current sound being analyzed
        self.current_playing_label = ctk.CTkLabel(self, text=f"Plot for: {self.playing_sound.path}")
        self.current_playing_label.pack(pady=10)

        # Create a placeholder for the plot
        self.canvas = None

    def display_plot(self):
        # Make sure the playing sound path is valid
        if not self.playing_sound.path:
            return

        # Call VoiceActivityDetector to get the plot
        vad = VoiceActivityDetector(self.playing_sound)
        vad.detect_speech()  # Run the detection to generate data

        # Create a figure for the plot
        fig = plt.Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        # Plot the detected speech regions (customize based on VoiceActivityDetector logic)
        vad.plot_detected_speech_regions()

        # Create a canvas to embed the plot in the Tkinter frame
        if self.canvas:
            self.canvas.get_tk_widget().destroy()  # Clear the old canvas if any
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=10, pady=10)