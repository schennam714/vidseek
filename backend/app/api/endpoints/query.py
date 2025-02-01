from fastapi import APIRouter, Depends, HTTPException, Query
from ..services.embedding import embedding_service
from ..services.opensearch_service import opensearch_service
from typing import List, Optional
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

@router.post("/search", response_model=List[SearchResult])
async def search_media(
    query: str,
    k: int = Query(
        default=10,
        ge=1,
        le=20,
        description="Number of results to return. Min: 1, Max: 20"
    ),
    min_score: float = Query(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0-1)"
    )
):
    """
    Search through media chunks using semantic similarity.
    
    Parameters:
    - query: The search query text
    - k: Number of results to return (default: 3)
    - min_score: Minimum similarity score threshold (default: 0.7)
    
    Returns:
    - List of matching chunks with their timestamps and scores
    """
    try:
        # Generate embedding for the search query
        query_embedding = embedding_service.generate_embedding(query)
        
        # Search OpenSearch for similar chunks
        results = opensearch_service.search_similar(
            query_vector=query_embedding,
            k=k,
            min_score=min_score
        )
        
        # Filter and sort results
        filtered_results = [
            result for result in results 
            if result['score'] >= min_score
        ]
        
        return filtered_results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        ) 