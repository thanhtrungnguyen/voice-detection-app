import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sounddevice as sd
import librosa

# Set parameters for real-time processing
CHUNK_SIZE = 1024  # Number of audio frames per chunk
SAMPLE_RATE = 16000  # Sample rate for real-time audio
ENERGY_THRESHOLD_FACTOR = 1.5  # Factor to multiply RMS energy for VAD thresholding


class RealTimeVADApp:
    def __init__(self, master):
        self.master = master
        self.is_recording = False

        # GUI setup
        self.frame_left = ctk.CTkFrame(master=self.master)
        self.frame_left.pack(side=ctk.LEFT, fill=ctk.Y, padx=20, pady=20)

        self.frame_right = ctk.CTkFrame(master=self.master)
        self.frame_right.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=20, pady=20)

        self.start_button = ctk.CTkButton(master=self.frame_left, text="Start Listening", command=self.start_recording)
        self.start_button.pack(pady=20)

        self.stop_button = ctk.CTkButton(master=self.frame_left, text="Stop Listening", command=self.stop_recording)
        self.stop_button.pack(pady=20)

        # Matplotlib figure for the waveform
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_right)
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.ax.set_ylim([-1, 1])
        self.audio_data = np.zeros(CHUNK_SIZE)

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=SAMPLE_RATE,
                                         blocksize=CHUNK_SIZE)
            self.stream.start()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stream.stop()
            self.stream.close()

    def audio_callback(self, indata, frames, time, status):
        """Process audio chunks in real-time"""
        if status:
            print(status)

        # Flatten input audio data
        audio_chunk = indata[:, 0]

        # Append new audio chunk to buffer
        self.audio_data = np.concatenate((self.audio_data, audio_chunk))[
                          -CHUNK_SIZE * 5:]  # Keep a rolling window of 5 chunks

        # Perform VAD on the chunk
        vad = self.perform_vad(audio_chunk)

        # Plot the waveform and VAD result
        self.update_plot(vad)

    def perform_vad(self, audio_chunk):
        """Perform VAD on audio chunk using energy thresholding"""
        energy = librosa.feature.rms(y=audio_chunk)[0]
        threshold = np.mean(energy) * ENERGY_THRESHOLD_FACTOR
        vad = (energy > threshold).astype(int)
        return vad

    def update_plot(self, vad):
        """Update the plot with the audio data and VAD highlights"""
        self.ax.clear()

        # Plot audio waveform
        time_axis = np.linspace(0, len(self.audio_data) / SAMPLE_RATE, len(self.audio_data))
        self.ax.plot(time_axis, self.audio_data, color='blue')

        # Overlay the VAD (highlight detected speech regions)
        chunk_time_axis = np.linspace(0, CHUNK_SIZE / SAMPLE_RATE, len(vad))
        for i in range(len(vad) - 1):
            if vad[i] == 1:
                self.ax.axvspan(chunk_time_axis[i], chunk_time_axis[i + 1], color='green', alpha=0.3)

        self.ax.set_ylim([-1, 1])
        self.ax.set_xlim([0, len(self.audio_data) / SAMPLE_RATE])
        self.canvas.draw()


# Main App
app = ctk.CTk()
app.geometry("800x600")
app.title("Real-Time Voice Activity Detection")

vad_app = RealTimeVADApp(app)

app.mainloop()
