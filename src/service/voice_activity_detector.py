import numpy as np
import scipy.io.wavfile as wf
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

from src.model.playing_sound import PlayingSound


class VoiceActivityDetector:
    """ Use signal energy to detect voice activity in a wav file """

    def __init__(self, playing_sound: PlayingSound):
        """
        Initializes the VoiceActivityDetector with a playing sound object.
        Reads and processes the wav file, and sets various parameters for voice detection.

        :param playing_sound: PlayingSound object that holds the path of the sound file.
        """
        self.wave_input_filename: str = playing_sound.path
        self.playing_sound: PlayingSound = playing_sound

        # Read the wav file and convert to mono if necessary
        self._read_wav(self.wave_input_filename)._convert_to_mono()

        # Configuration parameters for detection
        self.sample_window: float = 0.02  # Window size of 20 ms
        self.sample_overlap: float = 0.01  # Overlap size of 10 ms
        self.speech_window: float = 0.5  # Speech detection smoothing window (0.5 seconds)
        self.speech_energy_threshold: float = 0.3  # Energy threshold for speech detection (30%)
        self.speech_start_band: int = 300  # Minimum frequency for speech detection (300 Hz)
        self.speech_end_band: int = 3000  # Maximum frequency for speech detection (3000 Hz)

    def _read_wav(self, wave_file: str) -> 'VoiceActivityDetector':
        """
        Reads a wav file and extracts its sample rate and data.

        :param wave_file: The path to the wav file.
        :return: self for method chaining.
        """
        self.rate: int
        self.data: np.ndarray
        self.rate, self.data = wf.read(wave_file)
        self.channels: int = len(self.data.shape)  # Number of audio channels (1 for mono, 2 for stereo)
        self.filename: str = wave_file
        return self

    def _convert_to_mono(self) -> 'VoiceActivityDetector':
        """
        Converts stereo audio data to mono by averaging the two channels.

        :return: self for method chaining.
        """
        if self.channels == 2:
            # If audio data is stereo (2 channels), convert to mono by averaging both channels
            self.data = np.mean(self.data, axis=1, dtype=self.data.dtype)
            self.channels = 1  # Set the channel count to 1 (mono)
        return self

    def _calculate_frequencies(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Calculates the frequency components of the given audio data using FFT.

        :param audio_data: The audio data for which frequencies are computed.
        :return: Array of frequency components.
        """
        # Calculate the frequency components using FFT (Fast Fourier Transform)
        data_freq: np.ndarray = np.fft.fftfreq(len(audio_data), 1.0 / self.rate)
        # Discard the zero frequency component (DC component)
        data_freq = data_freq[1:]
        return data_freq

    def _calculate_amplitude(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Computes the amplitude of the frequency components using FFT.

        :param audio_data: The audio data to analyze.
        :return: Array of amplitudes corresponding to each frequency.
        """
        # Apply FFT to compute the amplitude (magnitude) of each frequency component
        data_ampl: np.ndarray = np.abs(np.fft.fft(audio_data))
        # Ignore the zero frequency component (DC component)
        data_ampl = data_ampl[1:]
        return data_ampl

    def _calculate_energy(self, data: np.ndarray) -> np.ndarray:
        """
        Calculates the energy (amplitude squared) of the audio data.

        :param data: The audio data to analyze.
        :return: Array of energy values corresponding to each frequency.
        """
        # Calculate amplitude using FFT
        data_amplitude: np.ndarray = self._calculate_amplitude(data)
        # Energy is the square of the amplitude
        data_energy: np.ndarray = data_amplitude ** 2
        return data_energy

    def _znormalize_energy(self, data_energy: np.ndarray) -> np.ndarray:
        """
        Z-normalizes the energy values to standardize them (zero mean, unit variance).

        :param data_energy: The energy data to normalize.
        :return: Z-normalized energy values.
        """
        # Calculate the mean and standard deviation of the energy values
        energy_mean: float = np.mean(data_energy)
        energy_std: float = np.std(data_energy)
        # Apply Z-normalization to center and scale the data
        energy_znorm: np.ndarray = (data_energy - energy_mean) / energy_std
        return energy_znorm

    def _connect_energy_with_frequencies(self, data_freq: np.ndarray, data_energy: np.ndarray) -> Dict[float, float]:
        """
        Connects the energy values with their corresponding frequencies.

        :param data_freq: Array of frequencies.
        :param data_energy: Array of energy values.
        :return: Dictionary mapping frequencies to their energy.
        """
        # Create a dictionary to map absolute frequency values to their energy values
        energy_freq: Dict[float, float] = {}
        for i, freq in enumerate(data_freq):
            if abs(freq) not in energy_freq:
                # For symmetry, double the energy value for positive frequencies
                energy_freq[abs(freq)] = data_energy[i] * 2
        return energy_freq

    def _calculate_normalized_energy(self, data: np.ndarray) -> Dict[float, float]:
        """
        Calculates and returns the normalized energy mapped to corresponding frequencies.

        :param data: The audio data to analyze.
        :return: Dictionary mapping frequencies to their normalized energy.
        """
        # First, calculate the frequency components of the audio data
        data_freq: np.ndarray = self._calculate_frequencies(data)
        # Then calculate the energy for the corresponding frequency components
        data_energy: np.ndarray = self._calculate_energy(data)
        # (Optional step: Normalize the energy if needed)
        # Map the calculated energy to the corresponding frequencies
        energy_freq: Dict[float, float] = self._connect_energy_with_frequencies(data_freq, data_energy)
        return energy_freq

    def _sum_energy_in_band(self, energy_frequencies: Dict[float, float], start_band: int, end_band: int) -> float:
        """
        Sums the energy in a given frequency band.

        :param energy_frequencies: Dictionary mapping frequencies to their energy.
        :param start_band: The start of the frequency band.
        :param end_band: The end of the frequency band.
        :return: Sum of energy in the specified band.
        """
        sum_energy: float = 0
        # Iterate through the frequency-energy mapping and sum the energy in the desired band
        for f in energy_frequencies.keys():
            if start_band < f < end_band:
                sum_energy += energy_frequencies[f]
        return sum_energy

    def _median_filter(self, x: np.ndarray, k: int) -> np.ndarray:
        """
        Applies a median filter to the input signal.

        :param x: The input data (1D array).
        :param k: The size of the median filter (must be odd).
        :return: The filtered data.
        """
        assert k % 2 == 1, "Median filter length must be odd."  # Ensure odd filter size
        assert x.ndim == 1, "Input must be one-dimensional."  # Ensure input is 1D

        k2: int = (k - 1) // 2
        # Create a buffer matrix to store the sliding window values for the median filter
        y: np.ndarray = np.zeros((len(x), k), dtype=x.dtype)
        y[:, k2] = x  # Set the central column to the original data

        # Fill the buffer with shifted versions of the input data for the median filter
        for i in range(k2):
            j: int = k2 - i
            y[j:, i] = x[:-j]  # Shift right
            y[:j, i] = x[0]    # Pad the beginning with the first value
            y[:-j, -(i + 1)] = x[j:]  # Shift left
            y[-j:, -(i + 1)] = x[-1]  # Pad the end with the last value

        # Return the median of the windowed values for each point in the input
        return np.median(y, axis=1)

    def _smooth_speech_detection(self, detected_windows: np.ndarray) -> np.ndarray:
        """
        Smooths the detected speech windows using a median filter to reduce noise.

        :param detected_windows: Detected speech windows with start indices and speech flags.
        :return: Smoothed speech flags.
        """
        # Calculate the number of windows in the smoothing window size (speech_window)
        median_window: int = int(self.speech_window / self.sample_window)
        if median_window % 2 == 0:
            median_window = median_window - 1  # Ensure the filter size is odd
        # Apply a median filter to the speech detection results to smooth noise
        median_energy: np.ndarray = self._median_filter(detected_windows[:, 1], median_window)
        return median_energy

    def convert_windows_to_readible_labels(self, detected_windows: np.ndarray) -> List[Dict[str, float]]:
        """
        Converts detected speech windows into readable time intervals.

        :param detected_windows: Array of window numbers and speech flags.
        :return: List of dictionaries with speech intervals.
        """
        speech_time: List[Dict[str, float]] = []
        is_speech: int = 0  # Keeps track if speech is currently being detected

        # Iterate through each window to detect the start and end times of speech segments
        for window in detected_windows:
            if window[1] == 1.0 and is_speech == 0:  # Detect start of speech
                is_speech = 1
                speech_label: Dict[str, float] = {}
                speech_time_start: float = window[0] / self.rate  # Convert sample index to time in seconds
                speech_label['speech_begin'] = speech_time_start
                print(window[0], speech_time_start)
            if window[1] == 0.0 and is_speech == 1:  # Detect end of speech
                is_speech = 0
                speech_time_end: float = window[0] / self.rate  # Convert sample index to time in seconds
                speech_label['speech_end'] = speech_time_end
                speech_time.append(speech_label)
                print(window[0], speech_time_end)

        return speech_time

    # def plot_detected_speech_regions(self) -> 'VoiceActivityDetector':
    #     """
    #     Plots the original signal and detected speech regions.
    #
    #     :return: self for method chaining.
    #     """
    #     data: np.ndarray = self.data
    #     detected_windows: np.ndarray = self.detect_speech()  # Detect speech regions
    #     data_speech: np.ndarray = np.zeros(len(data))  # Initialize array to store detected speech
    #
    #     # Highlight detected speech regions by multiplying original signal with speech flags
    #     it = np.nditer(detected_windows[:, 0], flags=['f_index'])
    #     while not it.finished:
    #         data_speech[int(it[0])] = data[int(it[0])] * detected_windows[it.index, 1]
    #         it.iternext()
    #     # Plot the original signal and detected speech regions for visualization
    #     plt.figure()
    #     plt.plot(data_speech)  # Plot detected speech regions
    #     plt.plot(data)         # Plot original signal
    #     plt.show()
    #     return self

    def plot_detected_speech_regions(self, ax):
        """Plots the detected speech regions on the provided matplotlib axes with more details."""
        # Prepare data for plotting
        data = self.data  # Original audio data
        detected_windows = self.detect_speech()  # Speech detection results

        # Create a speech-detected version of the data
        data_speech = np.zeros_like(data)
        for start, speech_flag in detected_windows:
            if speech_flag == 1:  # Speech detected
                data_speech[int(start)] = data[int(start)]

        # Plot the original signal and detected speech regions
        ax.plot(data, label="Original Signal", color='blue', alpha=0.5)
        ax.plot(data_speech, label="Detected Speech", color='red')

        # Add labels and title for clarity
        ax.set_title("Voice Activity Detection")
        ax.set_xlabel("Time (samples)")
        ax.set_ylabel("Amplitude")

        # Highlight the speech regions with shaded areas for better visualization
        speech_indices = np.where(data_speech != 0)[0]  # Get indices where speech is detected
        for start in speech_indices:
            ax.axvspan(start, start + len(data_speech) / len(detected_windows), color='red', alpha=0.1)

        # Add gridlines for better reading of the plot
        ax.grid(True)

        # Add a legend to describe the plot elements
        ax.legend()

        # Optionally: Make the plot interactive (zooming, etc.)
        plt.tight_layout()

    def detect_speech(self) -> np.ndarray:
        """
        Detects speech regions based on ratio between speech band energy
        and total energy.
        Output is array of window numbers and speech flags (1 - speech, 0 - non speech).
        """
        detected_windows: np.ndarray = np.array([])  # Array to store detected speech windows
        sample_window: int = int(self.rate * self.sample_window)  # Number of samples per window
        sample_overlap: int = int(self.rate * self.sample_overlap)  # Number of samples for window overlap
        data: np.ndarray = self.data
        sample_start: int = 0
        start_band: int = self.speech_start_band
        end_band: int = self.speech_end_band

        # Slide through the audio data in windows with overlap to detect speech
        while sample_start < (len(data) - sample_window):
            sample_end = sample_start + sample_window
            if sample_end >= len(data):
                sample_end = len(data) - 1
            # Extract the current window of data
            data_window: np.ndarray = data[sample_start:sample_end]
            # Calculate the normalized energy for the current window
            energy_freq: Dict[float, float] = self._calculate_normalized_energy(data_window)
            # Sum the energy within the speech band (e.g., 300Hz - 3000Hz)
            sum_voice_energy: float = self._sum_energy_in_band(energy_freq, start_band, end_band)
            # Sum the total energy across all frequencies
            sum_full_energy: float = sum(energy_freq.values())
            # Calculate the ratio of speech band energy to total energy
            speech_ratio: float = 0

            # Check for zero before dividing
            if sum_full_energy == 0:
                speech_ratio = 0  # Set speech_ratio to 0 if there's no full energy
            else:
                speech_ratio = sum_voice_energy / sum_full_energy

            # If the ratio exceeds the threshold, flag this window as containing speech
            speech_ratio = speech_ratio > self.speech_energy_threshold
            detected_windows = np.append(detected_windows, [sample_start, speech_ratio])
            # Move the window start by the overlap size
            sample_start += sample_overlap

        # Reshape the array to store window indices and corresponding speech flags
        detected_windows = detected_windows.reshape(int(len(detected_windows) / 2), 2)
        # Smooth the speech detection results using a median filter to reduce noise
        detected_windows[:, 1] = self._smooth_speech_detection(detected_windows)
        return detected_windows
