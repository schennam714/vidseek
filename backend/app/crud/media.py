from typing import List, Optional
from sqlalchemy.orm import Session
from .base import CRUDBase
from ..models.media import Media, Transcription, TranscriptionSegment, Chunk
from ..schemas.media import MediaCreate, MediaUpdate, TranscriptionCreate, TranscriptionSegmentCreate, ChunkCreate

class CRUDMedia(CRUDBase[Media, MediaCreate, MediaUpdate]):
    def create_with_transcription(
        self,
        db: Session,
        *,
        media: MediaCreate,
        segments: List[tuple],
        chunks: List[dict]
    ) -> Media:
        # Create media entry
        db_media = Media(
            filename=media.filename,
            file_path=media.file_path,
            audio_path=media.audio_path
        )
        db.add(db_media)
        db.flush()  # Get ID without committing

        # Create transcription
        db_transcription = Transcription(media_id=db_media.id)
        db.add(db_transcription)
        db.flush()

        # Create segments
        for text, start_time, end_time in segments:
            segment = TranscriptionSegment(
                transcription_id=db_transcription.id,
                text=text,
                start_time=start_time,
                end_time=end_time
            )
            db.add(segment)

        # Create chunks
        for chunk_data in chunks:
            chunk = Chunk(
                media_id=db_media.id,
                text=chunk_data["text"],
                start_time=chunk_data["start_time"],
                end_time=chunk_data["end_time"]
            )
            db.add(chunk)

        try:
            db.commit()
            db.refresh(db_media)
            return db_media
        except Exception as e:
            db.rollback()
            raise e

    def get_with_relations(self, db: Session, id: int) -> Optional[Media]:
        return db.query(Media).filter(Media.id == id).first()

crud_media = CRUDMedia(Media) 