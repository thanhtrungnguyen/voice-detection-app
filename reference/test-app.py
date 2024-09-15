import os
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AudioAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Audio Analyzer")
        self.geometry("800x600")

        # Frame for buttons
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20)

        # Button to load audio file
        self.load_button = ctk.CTkButton(self.frame, text="Load Audio File", command=self.load_audio)
        self.load_button.pack(pady=10)

        # Frame for the plot
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(pady=20, fill='both', expand=True)

        # Initialize the canvas for the plot
        self.canvas = None

    def load_audio(self):
        # Open file dialog to select audio file
        audio_file = ctk.filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.flac")])

        if audio_file:
            # Process the audio file
            self.process_audio(audio_file)

    def process_audio(self, audio_file):
        # Load the audio file
        data, sample_rate = sf.read(audio_file)

        # Parameters for voice activity detection
        frame_length = 2048
        hop_length = 512
        threshold = 0.02  # Adjust this threshold based on your needs

        # Calculate the short-time energy of the audio signal
        energy = np.array([
            np.sum(np.abs(data[i:i + frame_length] ** 2))
            for i in range(0, len(data) - frame_length + 1, hop_length)
        ])

        # Detect voice activity based on energy threshold
        voice_activity = energy > threshold

        # Generate time axis for plotting
        time = np.arange(len(energy)) * hop_length / sample_rate

        # Create a combined plot
        plt.figure(figsize=(10, 4))
        plt.plot(np.arange(len(data)) / sample_rate, data, color='b', label='Audio Signal')
        plt.title('Audio Signal Waveform with Voice Activity Detection')
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude')
        plt.grid()

        # Overlay voice activity detection
        plt.fill_between(time, np.min(data), np.max(data), where=voice_activity,
                         color='lightcoral', alpha=0.5, label='Voice Activity')

        plt.legend()

        # If there's an existing canvas, remove it
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        # Create a canvas for the plot and add it to the frame
        self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Clear the plot after embedding it in the Tkinter window
        plt.clf()


if __name__ == "__main__":
    app = AudioAnalyzerApp()
    app.mainloop()
