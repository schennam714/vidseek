import whisper
from fastapi import HTTPException
from typing import List, Tuple
import os
from ..core.config import settings

class TranscriptionService:
    def __init__(self):
        try:
            self.model = whisper.load_model("base")
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to load Whisper model: {str(e)}"
            )
    
    def transcribe_audio(self, audio_path: str) -> List[Tuple[str, float, float]]:
        try:
            # Transcribe audio
            result = self.model.transcribe(audio_path)
            
            # Extract segments with timestamps
            segments = []
            for segment in result["segments"]:
                segments.append((
                    segment["text"].strip(),
                    segment["start"],
                    segment["end"]
                ))
            
            return segments
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {str(e)}"
            ) 