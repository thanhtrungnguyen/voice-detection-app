import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.playback_line_waveform = None  # Line for playback position in waveform plot
        self.playback_line_energy = None  # Line for playback position in energy plot

        # Create a standard tk.Frame to hold the matplotlib plot
        self.plot_container = tk.Frame(self)
        self.plot_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Create the matplotlib figure with two subplots
        self.fig, (self.ax_waveform, self.ax_energy) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # Create the canvas and attach it to the tk.Frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def plot_waveform(self, audio_data, frame_rate, vad_result):
        """Plot the waveform and energy plot with VAD results."""
        self.ax_waveform.clear()
        self.ax_energy.clear()

        # Time axis in seconds
        time_axis = np.linspace(0, len(audio_data) / frame_rate, num=len(audio_data))

        # Plot waveform in the first subplot (ax_waveform)
        self.ax_waveform.plot(time_axis, audio_data, color='blue', label="Waveform", alpha=0.7)
        self.ax_waveform.set_ylabel("Amplitude", fontsize=12)
        self.ax_waveform.set_title(
            f"Audio Waveform with VAD - Total Duration: {len(audio_data) / frame_rate:.2f} seconds", fontsize=14,
            fontweight='bold')

        # Highlight speech segments based on VAD results
        self._highlight_vad_segments(time_axis, audio_data, vad_result, frame_rate)

        # Calculate and plot energy in the second subplot (ax_energy)
        energy = np.abs(audio_data)
        self.ax_energy.plot(time_axis, energy, color='green', label="Energy", alpha=0.7)
        self.ax_energy.set_ylabel("Energy", fontsize=12)
        self.ax_energy.set_xlabel("Time (seconds)", fontsize=12)

        # Plot formatting
        self.ax_waveform.grid(True)
        self.ax_energy.grid(True)

        # Link the x-axis for both plots
        self.ax_waveform.set_xlim(0, len(audio_data) / frame_rate)
        self.ax_energy.set_xlim(0, len(audio_data) / frame_rate)

        # Create playback indicator line, initially at time 0, in both subplots
        self.playback_line_waveform = self.ax_waveform.axvline(0, color='red', linestyle='-', label='Playback Position')
        self.playback_line_energy = self.ax_energy.axvline(0, color='red', linestyle='-')

        # Redraw the canvas
        self.fig.tight_layout()
        # self.canvas.draw()
        self.canvas.draw_idle()

    def update_playback_position(self, current_time):
        """Update the position of the playback line in both the waveform and energy plots."""
        if self.playback_line_waveform and self.playback_line_energy:
            # Update the position of both playback lines
            self.playback_line_waveform.set_xdata([current_time])  # Move the line to the current time in waveform plot
            self.playback_line_energy.set_xdata([current_time])  # Move the line to the current time in energy plot
            self.canvas.draw()

    def _highlight_vad_segments(self, time_axis, audio_data, vad_result, frame_rate):
        """Highlight the detected speech and non-speech segments in the waveform plot."""
        speech_color = 'red'
        speech_alpha = 0.2

        # Convert VAD result list into segments with start and end times
        speech_segments = []
        segment_start = None

        for i, is_speech in enumerate(vad_result):
            if is_speech and segment_start is None:
                segment_start = i
            elif not is_speech and segment_start is not None:
                speech_segments.append((segment_start, i))
                segment_start = None

        if segment_start is not None:
            speech_segments.append((segment_start, len(vad_result)))

        # Highlight detected speech segments in the waveform plot
        for start, end in speech_segments:
            start_time = start * (len(audio_data) / len(vad_result)) / frame_rate
            end_time = end * (len(audio_data) / len(vad_result)) / frame_rate
            self.ax_waveform.axvspan(start_time, end_time, color=speech_color, alpha=speech_alpha,
                                     label="Speech" if start == 0 else "")

        # Display markers for speech start and end boundaries
        # for start, end in speech_segments:
        #     start_time = start * (len(audio_data) / len(vad_result)) / frame_rate
        #     end_time = end * (len(audio_data) / len(vad_result)) / frame_rate
        #     self.ax_waveform.axvline(start_time, color='black', linestyle='--',
        #                              label="Speech Start" if start == 0 else "")
        #     self.ax_waveform.axvline(end_time, color='black', linestyle='--',
        #                              label="Speech End" if end == len(vad_result) else "")

        # Add label only once to avoid repetition in the legend
        handles, labels = self.ax_waveform.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))  # Remove duplicate labels
        self.ax_waveform.legend(by_label.values(), by_label.keys())
