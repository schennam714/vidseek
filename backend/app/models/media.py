from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    audio_path = Column(String)
    created_at = Column(Float, default=lambda: datetime.datetime.now().timestamp())
    
    # Relationships
    transcription = relationship("Transcription", back_populates="media", uselist=False)
    chunks = relationship("Chunk", back_populates="media")

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    
    # Relationships
    media = relationship("Media", back_populates="transcription")
    segments = relationship("TranscriptionSegment", back_populates="transcription")

class TranscriptionSegment(Base):
    __tablename__ = "transcription_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"))
    text = Column(Text)
    start_time = Column(Float)
    end_time = Column(Float)
    
    # Relationships
    transcription = relationship("Transcription", back_populates="segments")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    text = Column(Text)
    start_time = Column(Float)
    end_time = Column(Float)
    
    # Relationships
    media = relationship("Media", back_populates="chunks") 