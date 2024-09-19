# Audio-related constants
AUDIO_FILE_TYPES = [("WAV files", "*.wav")]

# App UI Labels
PLAY_BUTTON_LABEL = "Play"
PAUSE_BUTTON_LABEL = "Pause"
LOAD_BUTTON_LABEL = "Load Audio"

# App Name
APP_NAME = "Voice Activity Detection"

# UI Appearance Constants
WINDOW_TITLE = f"{APP_NAME} - Audio Player with Waveform and VAD"
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

# VAD Constants
VAD_SENSITIVITY = 1  # Sensitivity level for VAD (0 to 3)
FRAME_DURATION_MS = 30  # Frame duration in milliseconds for VAD processing

# Slider Configuration
SEEKBAR_MIN = 0
SEEKBAR_MAX = 100

# Waveform Plot
WAVEFORM_COLOR = 'blue'
VAD_HIGHLIGHT_COLOR = 'red'
VAD_HIGHLIGHT_ALPHA = 0.3

# Plot labels
PLOT_X_LABEL = "Time [s]"
PLOT_Y_LABEL = "Amplitude"
PLOT_TITLE = "Audio Waveform with Voice Activity Detection"
