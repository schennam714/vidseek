from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TranscriptionSegmentBase(BaseModel):
    text: str
    start_time: float
    end_time: float

class TranscriptionSegmentCreate(TranscriptionSegmentBase):
    pass

class TranscriptionSegmentInDB(TranscriptionSegmentBase):
    id: int
    transcription_id: int

    class Config:
        from_attributes = True

class ChunkBase(BaseModel):
    text: str
    start_time: float
    end_time: float

class ChunkCreate(ChunkBase):
    pass

class ChunkInDB(ChunkBase):
    id: int
    media_id: int

    class Config:
        from_attributes = True

class TranscriptionBase(BaseModel):
    pass

class TranscriptionCreate(TranscriptionBase):
    pass

class TranscriptionInDB(TranscriptionBase):
    id: int
    media_id: int
    segments: List[TranscriptionSegmentInDB]

    class Config:
        from_attributes = True

class MediaBase(BaseModel):
    filename: str
    file_path: str
    audio_path: str

class MediaCreate(MediaBase):
    pass

class MediaUpdate(BaseModel):
    filename: Optional[str] = None
    file_path: Optional[str] = None
    audio_path: Optional[str] = None

class MediaInDB(MediaBase):
    id: int
    created_at: float
    transcription: Optional[TranscriptionInDB]
    chunks: List[ChunkInDB]

    class Config:
        from_attributes = True 