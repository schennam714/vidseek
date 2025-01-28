from fastapi import APIRouter, UploadFile, File
from ...services.media_processor import MediaProcessor

router = APIRouter()

@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    file_path = await MediaProcessor.save_upload(file)
    audio_path = MediaProcessor.extract_audio(file_path)
    return {
        "filename": file.filename,
        "file_path": file_path,
        "audio_path": audio_path
    } 