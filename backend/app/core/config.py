from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Multimedia Query Tool"
    
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]
    
    UPLOAD_FOLDER: str = "uploads"
    DATABASE_URL: str = "sqlite:///./multimedia_query.db"
    
    CHUNK_SIZE_SECONDS: int = 30
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 