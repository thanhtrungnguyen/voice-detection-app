import webrtcvad
from src.constants.app_constants import FRAME_DURATION_MS
from src.utils.logger import get_logger


class VADService:
    def __init__(self, sensitivity):
        self.logger = get_logger(__name__)
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(sensitivity)  # Sensitivity: 0 (least sensitive) to 3 (most sensitive)
        self.logger.info(f"VAD Service initialized with sensitivity {sensitivity}.")

    def detect_voice_activity(self, audio_data, frame_rate, frame_duration=FRAME_DURATION_MS):
        """Detect voice activity in the audio data."""
        self.logger.info("Detecting voice activity.")
        if audio_data is None:
            return []

        vad_results = []
        frame_size = int(frame_rate * frame_duration / 1000)  # Number of samples per frame
        step_size = frame_size // 2  # 50% overlap

        # Process audio with overlapping frames
        for i in range(0, len(audio_data) - frame_size, step_size):
            frame = audio_data[i:i + frame_size].tobytes()

            # Check if the frame length is exactly the expected size
            if len(frame) == frame_size * 2:  # Each sample is 2 bytes (16-bit PCM)
                is_speech = self.vad.is_speech(frame, frame_rate)
                vad_results.append(is_speech)

        return vad_results
