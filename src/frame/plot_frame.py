import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.model.playing_sound import PlayingSound
from src.service.voice_activity_detector import VoiceActivityDetector


class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, playing_sound:PlayingSound):
        super().__init__(parent)
        self.place(relx=0.25, y=0, relwidth=0.75, relheight=1)

        # Store the PlayingSound object
        self.playing_sound = playing_sound

        # Create label for displaying the current sound being analyzed
        self.current_playing_label = ctk.CTkLabel(self, text=f"Plot for: {self.playing_sound.path}")
        self.current_playing_label.pack(pady=10)

        # Create a placeholder for the plot
        self.canvas = None

    def display_plot(self):
        if not self.playing_sound.path:
            return

        vad = VoiceActivityDetector(self.playing_sound)
        vad.detect_speech()  # Run detection to generate data

        # Create the figure and axis for plotting
        fig, ax = plt.subplots(figsize=(12, 7))

        # Pass the axis to the VoiceActivityDetector for detailed plotting
        vad.plot_detected_speech_regions(ax)

        # Embed the plot in the Tkinter frame
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=10, pady=10)
