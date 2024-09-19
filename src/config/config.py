import customtkinter as ctk
from src.constants.app_constants import VAD_SENSITIVITY


class AppConfig:
    """Configuration class for application settings."""

    def __init__(self, mode="development"):
        self.mode = mode

    def load_config(self):
        """Load configuration settings based on the mode."""
        if self.mode == "development":
            self.load_development_config()
        elif self.mode == "production":
            self.load_production_config()
        else:
            self.load_default_config()

    def load_development_config(self):
        """Settings for development mode."""
        print("Loading Development Configuration")
        ctk.set_appearance_mode("dark")  # Dark mode for development
        ctk.set_default_color_theme("blue")

    def load_production_config(self):
        """Settings for production mode."""
        print("Loading Production Configuration")
        ctk.set_appearance_mode("light")  # Light mode for production
        ctk.set_default_color_theme("green")

    def load_default_config(self):
        """Load default settings."""
        print("Loading Default Configuration")
        ctk.set_appearance_mode("system")  # Follows system mode
        ctk.set_default_color_theme("blue")

    @staticmethod
    def get_vad_sensitivity():
        """Get the VAD sensitivity setting."""
        return VAD_SENSITIVITY
