from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from ..core.config import settings

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def generate_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for a single text or list of texts
        """
        try:
            embeddings = self.model.encode(text, normalize_embeddings=True)
            #print(text, embeddings)
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for a list of texts in batches
        """
        try:
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.generate_embedding(batch)
                embeddings.extend(batch_embeddings)
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating batch embeddings: {str(e)}")

embedding_service = EmbeddingService() 