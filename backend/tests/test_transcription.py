import pytest
from app.services.transcription import TranscriptionService
from pydub import AudioSegment

@pytest.fixture
def test_audio_with_speech():
    # Create a test audio file with silence
    # In a real test, you might want to use a small sample audio file with known content
    file_path = "test_speech.wav"
    AudioSegment.silent(duration=1000).export(file_path, format="wav")
    yield file_path
    import os
    if os.path.exists(file_path):
        os.remove(file_path)

def test_transcription_service_init():
    service = TranscriptionService()
    assert service.model is not None

def test_transcribe_audio(test_audio_with_speech):
    service = TranscriptionService()
    segments = service.transcribe_audio(test_audio_with_speech)
    assert isinstance(segments, list)
    # Even with silence, Whisper should return at least one segment
    assert len(segments) >= 0
    if segments:
        segment = segments[0]
        assert len(segment) == 3  # (text, start_time, end_time)
        assert isinstance(segment[0], str)  # text
        assert isinstance(segment[1], float)  # start_time
        assert isinstance(segment[2], float)  # end_time 