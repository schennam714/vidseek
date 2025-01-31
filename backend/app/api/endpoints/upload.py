from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ...services.media_processor import MediaProcessor
from ...services.transcription import TranscriptionService
from ...services.chunking import ChunkingService
from ...crud import crud_media
from ...schemas.media import MediaCreate, MediaInDB
from ...db.session import get_db
from typing import List

router = APIRouter()
transcription_service = TranscriptionService()
chunking_service = ChunkingService()

@router.post("/upload", response_model=MediaInDB)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a media file, process it, and store results in database.
    """
    try:
        # Save and process file
        file_path = await MediaProcessor.save_upload(file)
        audio_path = MediaProcessor.extract_audio(file_path)
        
        # Transcribe audio
        segments = transcription_service.transcribe_audio(audio_path)
        
        # Create chunks
        chunks = chunking_service.create_chunks(segments)
        
        # Prepare media data
        media_create = MediaCreate(
            filename=file.filename,
            file_path=file_path,
            audio_path=audio_path
        )
        
        # Save to database with transcription and chunks
        db_media = crud_media.create_with_transcription(
            db=db,
            media=media_create,
            segments=segments,
            chunks=[{
                "text": chunk.text,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time
            } for chunk in chunks]
        )
        
        return db_media
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing media: {str(e)}"
        )

@router.get("/{media_id}", response_model=MediaInDB)
async def get_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve media and its associated transcription/chunks by ID.
    """
    db_media = crud_media.get_with_relations(db, media_id)
    if not db_media:
        raise HTTPException(
            status_code=404,
            detail="Media not found"
        )
    return db_media

@router.get("/", response_model=List[MediaInDB])
async def list_media(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List all media files with their transcriptions and chunks.
    """
    return crud_media.get_multi(db, skip=skip, limit=limit)

@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a media file and its associated data.
    """
    try:
        media = crud_media.remove(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=404,
                detail="Media not found"
            )
        # Also delete the physical files
        MediaProcessor.delete_files(media.file_path, media.audio_path)
        return {"message": "Media deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting media: {str(e)}"
        ) 