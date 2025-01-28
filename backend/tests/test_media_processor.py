import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
from app.main import app
from app.services.media_processor import MediaProcessor
from pydub import AudioSegment

client = TestClient(app)

@pytest.fixture
def test_file():
    file_path = "test_audio.mp3"
    # Create a 1-second silent MP3
    AudioSegment.silent(duration=1000).export(file_path, format="mp3")
    yield file_path
    os.remove(file_path)
    
@pytest.fixture
def invalid_file():
    file_path = "test_file.txt"
    with open(file_path, "wb") as f:
        f.write(b"test content")
    yield file_path
    os.remove(file_path)

def test_upload_valid_file(test_file):
    with open(test_file, "rb") as f:
        response = client.post(
            "/api/v1/media/upload",
            files={"file": ("test_audio.mp3", f, "audio/mpeg")}
        )
    assert response.status_code == 200
    assert "filename" in response.json()
    assert "file_path" in response.json()
    
    uploaded_path = response.json()["file_path"]
    if os.path.exists(uploaded_path):
        os.remove(uploaded_path)

def test_upload_invalid_extension(invalid_file):
    with open(invalid_file, "rb") as f:
        response = client.post(
            "/api/v1/media/upload",
            files={"file": ("test_file.txt", f, "text/plain")}
        )
    assert response.status_code == 400
    assert "File type not allowed" in response.json()["detail"]

def test_audio_extraction(test_file):
    with open(test_file, "rb") as f:
        response = client.post(
            "/api/v1/media/upload",
            files={"file": ("test_audio.mp3", f, "audio/mpeg")}
        )
    assert response.status_code == 200
    assert "audio_path" in response.json()
    
    # Cleanup files
    for path in [response.json()["file_path"], response.json()["audio_path"]]:
        if os.path.exists(path):
            os.remove(path) 