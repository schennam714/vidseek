from ...services.embedding import embedding_service
from ...services.opensearch_service import opensearch_service
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from pydantic import BaseModel

router = APIRouter()

class SearchResult(BaseModel):
    text: str
    media_id: str
    start_time: float
    end_time: float
    score: float
    
    class Config:
        from_attributes = True

@router.post("/search")
async def search_media(query: str, min_score: float = 0.6, k: int = 3):
    try:
        # Generate embedding for query
        query_vector = embedding_service.generate_embedding(query)
        
        # Search OpenSearch
        results = opensearch_service.search_similar(
            query_vector=query_vector,
            query_text=query,
            k=k,
            min_score=min_score
        )
        
        return results  # Return the list directly instead of grouping by media_id
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 