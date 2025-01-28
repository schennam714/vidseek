from fastapi import APIRouter, UploadFile, File
from ...services.media_processor import MediaProcessor
from ...services.transcription import TranscriptionService

router = APIRouter()
transcription_service = TranscriptionService()

@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    # Save and process file
    file_path = await MediaProcessor.save_upload(file)
    audio_path = MediaProcessor.extract_audio(file_path)
    
    # Transcribe audio
    segments = transcription_service.transcribe_audio(audio_path)
    
    return {
        "filename": file.filename,
        "file_path": file_path,
        "audio_path": audio_path,
        "transcription": segments
    } 