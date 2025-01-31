from fastapi import APIRouter, UploadFile, File
from ...services.media_processor import MediaProcessor
from ...services.transcription import TranscriptionService
from ...services.chunking import ChunkingService
from ...core.config import settings

router = APIRouter()
transcription_service = TranscriptionService()
chunking_service = ChunkingService()  # Initialize the chunking service

@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    # Save and process file
    file_path = await MediaProcessor.save_upload(file)
    audio_path = MediaProcessor.extract_audio(file_path)
    
    # Transcribe audio
    segments = transcription_service.transcribe_audio(audio_path)
    
    # Create chunks from segments
    chunks = chunking_service.create_chunks(segments)
    
    return {
        "filename": file.filename,
        "file_path": file_path,
        "audio_path": audio_path,
        "transcription": segments,
        "chunks": [
            {
                "text": chunk.text,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time,
                "segment_ids": chunk.segment_ids
            }
            for chunk in chunks
        ]
    } 