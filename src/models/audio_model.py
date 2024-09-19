import pygame
from pydub import AudioSegment
import numpy as np


class AudioPlayerModel:
    def __init__(self, vad_service):
        pygame.mixer.init()
        self.audio_data = None
        self.frame_rate = None
        self.is_playing = False
        self.vad_service = vad_service

    def load_audio(self, file_path):
        """Load and preprocess the audio file."""
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        raw_data = audio.raw_data
        self.audio_data = np.frombuffer(raw_data, dtype=np.int16)
        self.frame_rate = 16000

        # Load the audio for playback using pygame
        pygame.mixer.music.load(file_path)

    def play_pause(self):
        """Toggle play and pause for the audio."""
        if self.is_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause() if pygame.mixer.music.get_busy() else pygame.mixer.music.play()
        self.is_playing = not self.is_playing
        return self.is_playing

    def seek(self, position):
        """Seek the audio to the selected position."""
        if self.audio_data is not None:
            pygame.mixer.music.play(start=position / self.frame_rate)

    def get_audio_data(self):
        return self.audio_data, self.frame_rate

    def get_current_playback_time(self):
        """Get the current playback time in seconds."""
        return pygame.mixer.music.get_pos() / 1000.0  # get_pos() returns milliseconds

    def detect_voice_activity(self):
        """Detect voice activity in the preprocessed audio."""
        return self.vad_service.detect_voice_activity(self.audio_data, self.frame_rate)

    def get_audio_duration(self):
        """Get the total duration of the audio in seconds."""
        return len(self.audio_data) / self.frame_rate
