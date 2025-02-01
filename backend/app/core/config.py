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
    DATABASE_URL: str = "sqlite:///multimedia_query.db"
    
    # Chunking settings
    CHUNK_SIZE_SECONDS: int = 30
    CHUNK_TARGET_SIZE: int = 200  # Target size in characters
    CHUNK_OVERLAP_SIZE: int = 5   # Number of overlapping sentences
    
    # OpenSearch Settings
    OPENSEARCH_HOST: str = os.getenv("OPENSEARCH_HOST", "")
    OPENSEARCH_PORT: int = int(os.getenv("OPENSEARCH_PORT", "443"))
    OPENSEARCH_INDEX: str = os.getenv("OPENSEARCH_INDEX", "media-chunks")
    OPENSEARCH_USER: str = os.getenv("OPENSEARCH_USER", "")
    OPENSEARCH_PASSWORD: str = os.getenv("OPENSEARCH_PASSWORD", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Embedding Settings
    EMBEDDING_DIMENSION: int = 384  # for 'all-MiniLM-L6-v2'
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 