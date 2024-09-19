import pytest
from src.models.audio_model import AudioPlayerModel
from src.services.vad_service import VADService


@pytest.fixture
def audio_model():
    vad_service = VADService(sensitivity=1)
    return AudioPlayerModel(vad_service)


def test_load_audio(audio_model):
    """Test if the audio file is loaded correctly."""
    audio_model.load_audio("path/to/test/audio.wav")  # Use a valid test file
    assert audio_model.audio_data is not None
    assert audio_model.frame_rate > 0


def test_voice_activity_detection(audio_model):
    """Test voice activity detection."""
    audio_model.load_audio("path/to/test/audio.wav")  # Use a valid test file
    vad_results = audio_model.detect_voice_activity()
    assert isinstance(vad_results, list)
    assert all(isinstance(result, bool) for result in vad_results)
