import pytest
from src.services.vad_service import VADService


@pytest.fixture
def vad_service():
    return VADService(sensitivity=1)


def test_vad_service(vad_service):
    """Test VAD service with a small sample."""
    test_audio = b'\x00\x01' * 8000  # Simulated raw audio data
    frame_rate = 16000
    vad_results = vad_service.detect_voice_activity(test_audio, frame_rate)
    assert isinstance(vad_results, list)
    assert len(vad_results) > 0
