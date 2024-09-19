import customtkinter as ctk
from src.views.audio_player_frame import AudioPlayerFrame
from src.views.plot_frame import PlotFrame
from src.controllers.audio_controller import AudioPlayerController
from src.models.audio_model import AudioPlayerModel
from src.services.vad_service import VADService
from src.models.audio_model import AudioPlayerModel
from src.controllers.audio_controller import AudioPlayerController
from src.services.vad_service import VADService
from src.config.config import AppConfig
from src.constants.app_constants import (
    PLAY_BUTTON_LABEL, PAUSE_BUTTON_LABEL, LOAD_BUTTON_LABEL, AUDIO_FILE_TYPES,
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, SEEKBAR_MIN, SEEKBAR_MAX
)


class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Load configuration for the app
        config = AppConfig(mode="development")  # Set mode as "development" or "production"
        config.load_config()

        # Initialize the VAD service and model
        vad_service = VADService(sensitivity=config.get_vad_sensitivity())
        model = AudioPlayerModel(vad_service)

        # Create frames
        self.audio_frame = AudioPlayerFrame(self, None)
        self.audio_frame.pack(side='left', padx=10, pady=10)

        self.plot_frame = PlotFrame(self, None)
        self.plot_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Initialize controller with both frames
        controller = AudioPlayerController(model, self.audio_frame, self.plot_frame)

        # Set controller in frames
        self.audio_frame.controller = controller
        self.plot_frame.controller = controller
