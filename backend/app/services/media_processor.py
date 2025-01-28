import os
from fastapi import UploadFile, HTTPException
from pydub import AudioSegment
from ..core.config import settings

class MediaProcessor:
    ALLOWED_EXTENSIONS = {'.mp4', '.mp3', '.wav', '.avi', '.mkv'}
    
    @staticmethod
    async def save_upload(file: UploadFile) -> str:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in MediaProcessor.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {MediaProcessor.ALLOWED_EXTENSIONS}"
            )
        
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        # Generate file path
        file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
        
        # Save
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    @staticmethod
    def extract_audio(file_path: str) -> str:
        try:
            # Generate output path
            filename = os.path.splitext(os.path.basename(file_path))[0]
            audio_path = os.path.join(settings.UPLOAD_FOLDER, f"{filename}.wav")
            
            # Extract audio based on input format
            if file_path.endswith('.mp4') or file_path.endswith('.avi') or file_path.endswith('.mkv'):
                video = AudioSegment.from_file(file_path)
                audio = video.set_channels(1)  # Convert to mono
                audio.export(audio_path, format="wav")
            elif file_path.endswith('.mp3'):
                audio = AudioSegment.from_mp3(file_path)
                audio = audio.set_channels(1)  # Convert to mono
                audio.export(audio_path, format="wav")
            elif file_path.endswith('.wav'):
                audio = AudioSegment.from_wav(file_path)
                if audio.channels > 1:
                    audio = audio.set_channels(1)  # Convert to mono if needed
                    audio.export(audio_path, format="wav")
                else:
                    return file_path  
                    
            return audio_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting audio: {str(e)}") 