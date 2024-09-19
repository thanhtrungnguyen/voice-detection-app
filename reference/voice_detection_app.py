import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pyaudio
from threading import Thread
import matplotlib.animation as animation
from scipy.signal import spectrogram


class VoiceDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sound Visualization and Voice Detection")
        self.root.geometry("1200x900")

        # Initialize parameters
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.fs = 44100  # Record at 44100 samples per second
        self.nperseg = 128  # Segment length for spectrogram

        # Set up the Matplotlib Figure
        self.fig, self.ax_waveform, self.ax_energy, self.ax_spectrogram = self.create_figure()

        # Create the canvas for plotting
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=1)

        # Add titles for the graphs below each one
        self.add_graph_labels()

        # Initialize data arrays
        self.data = np.zeros(self.chunk)
        self.energy_data = np.zeros(100)
        self.frequencies, self.times, Sxx = spectrogram(self.data, fs=self.fs, nperseg=self.nperseg, noverlap=self.nperseg // 2)
        self.spectrogram_data = np.zeros((len(self.frequencies), 100))

        # Audio stream setup
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.fs,
                                  input=True,
                                  frames_per_buffer=self.chunk)

        # Start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=50, cache_frame_data=False)

        # Start a separate thread for audio processing
        self.running = True
        self.audio_thread = Thread(target=self.process_audio)
        self.audio_thread.start()

    def create_figure(self):
        """Create a figure with three subplots for waveform, RMS energy, and spectrogram."""
        fig = Figure(figsize=(8, 6), dpi=100)

        # Waveform subplot
        ax_waveform = fig.add_subplot(311)
        ax_waveform.set_ylim(-32768, 32767)
        ax_waveform.set_xlim(0, self.chunk)
        ax_waveform.set_ylabel("Amplitude")
        ax_waveform.set_xlabel("Waveform (Amplitude)")  # Nhãn dưới chân
        ax_waveform.set_title("Waveform")

        # RMS Energy subplot
        ax_energy = fig.add_subplot(312)
        ax_energy.set_ylim(0, 1)
        ax_energy.set_xlim(0, 100)
        ax_energy.set_ylabel("RMS Energy")
        ax_energy.set_xlabel("RMS Energy (Normalized)")  # Nhãn dưới chân
        ax_energy.set_title("RMS Energy")

        # Spectrogram subplot
        ax_spectrogram = fig.add_subplot(313)
        ax_spectrogram.set_ylim(0, self.fs // 2)
        ax_spectrogram.set_xlim(0, 100)
        ax_spectrogram.set_ylabel("Frequency (Hz)")
        ax_spectrogram.set_xlabel("Spectrogram (Frequency in Hz)")  # Nhãn dưới chân
        ax_spectrogram.set_title("Spectrogram")

        fig.tight_layout()  # Căn chỉnh layout để không bị chồng chéo giữa các nhãn và biểu đồ

        return fig, ax_waveform, ax_energy, ax_spectrogram

    def add_graph_labels(self):
        """Add labels for each graph below them."""
        # Create a frame to hold the labels
        label_frame = ctk.CTkFrame(self.root)
        label_frame.pack(side=ctk.TOP, fill=ctk.X)

        # Waveform title
        waveform_label = ctk.CTkLabel(label_frame, text="Waveform (Amplitude)", font=("Arial", 16))
        waveform_label.pack(side=ctk.TOP, pady=(10, 5))

        # Energy title
        energy_label = ctk.CTkLabel(label_frame, text="RMS Energy (Normalized)", font=("Arial", 16))
        energy_label.pack(side=ctk.TOP, pady=(10, 5))

        # Spectrogram title
        spectrogram_label = ctk.CTkLabel(label_frame, text="Spectrogram (Frequency in Hz)", font=("Arial", 16))
        spectrogram_label.pack(side=ctk.TOP, pady=(10, 5))

    def process_audio(self):
        while self.running:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            np_data = np.frombuffer(data, dtype=np.int16)

            # Update waveform data
            self.data = np_data

            # Calculate RMS energy with safe handling for sqrt
            rms_energy = np.sqrt(np.abs(np.mean(np_data ** 2)))
            self.energy_data = np.append(self.energy_data[1:], rms_energy / 32768)

            # Calculate spectrogram (Short-time Fourier transform)
            f, t, Sxx = spectrogram(np_data, fs=self.fs, nperseg=self.nperseg, noverlap=self.nperseg // 2)
            Sxx = np.log(Sxx + 1e-10)  # Logarithmic scale for better visualization
            self.spectrogram_data = np.roll(self.spectrogram_data, -1, axis=1)
            self.spectrogram_data[:, -1] = Sxx.mean(axis=1)  # Update spectrogram data

    def update_plot(self, frame):
        # Update waveform plot
        self.ax_waveform.clear()
        self.ax_waveform.plot(self.data)
        self.ax_waveform.set_ylim(-32768, 32767)
        self.ax_waveform.set_xlim(0, len(self.data))

        # Update RMS energy plot
        self.ax_energy.clear()
        self.ax_energy.plot(self.energy_data)
        self.ax_energy.set_ylim(0, 1)
        self.ax_energy.set_xlim(0, 100)

        # Update spectrogram plot
        self.ax_spectrogram.clear()
        self.ax_spectrogram.imshow(self.spectrogram_data, aspect='auto', origin='lower',
                                   extent=[0, 100, 0, self.fs // 2], cmap='viridis')
        self.ax_spectrogram.set_ylim(0, self.fs // 2)
        self.ax_spectrogram.set_xlim(0, 100)

        # Redraw the canvas
        self.canvas.draw()

    def on_closing(self):
        self.running = False
        self.audio_thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.root.destroy()


# Initialize the customtkinter app
ctk.set_appearance_mode("System")  # Set the appearance mode to System (Dark/Light)
ctk.set_default_color_theme("blue")  # Set the color theme to blue

root = ctk.CTk()  # Use CTk instead of Tk
app = VoiceDetectionApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()