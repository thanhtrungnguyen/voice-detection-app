class AudioPlayerController:
    def __init__(self, model, audio_frame, plot_frame):
        """Initialize the controller with model and view frames."""
        self.model = model
        self.audio_frame = audio_frame
        self.plot_frame = plot_frame
        self.current_audio_file = None
        self.update_interval = 50

    def load_audio(self, file_name):
        """Load the selected audio file and prepare to plot."""
        self.model.load_audio(file_name)
        self.current_audio_file = file_name
        self.plot_audio()

    def play_audio(self):
        """Play the current audio file and start updating the playback line."""
        if self.current_audio_file:
            self.model.play_pause()
            if self.model.is_playing:
                self.update_playback_line()
                self.update_progress_bar()

    def plot_audio(self):
        """Plot the waveform and VAD results."""
        audio_data, frame_rate = self.model.get_audio_data()
        vad_result = self.model.detect_voice_activity()
        self.plot_frame.plot_waveform(audio_data, frame_rate, vad_result)

    def update_playback_line(self):
        """Update the playback line on the plot every 100ms."""
        if self.model.is_playing:
            current_time = self.model.get_current_playback_time()  # Get current playback time in seconds
            self.plot_frame.update_playback_position(current_time)

            # Schedule the next update after 100ms
            self.plot_frame.after(self.update_interval, self.update_playback_line)

    def update_progress_bar(self):
        """Update the progress bar and time labels every 100ms."""
        if self.model.is_playing:
            current_time = self.model.get_current_playback_time()  # Get current playback time in seconds
            total_time = self.model.get_audio_duration()  # Get total duration of the audio
            self.audio_frame.update_progress_bar(current_time, total_time)

            # Schedule the next update after 100ms
            self.audio_frame.after(self.update_interval, self.update_progress_bar)

    def seek_audio(self, new_time):
        """Seek the audio to a new position."""
        self.model.seek(new_time)
