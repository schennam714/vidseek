from opensearchpy import OpenSearch, RequestsHttpConnection
from typing import List, Dict, Any
import numpy as np
from ..core.config import settings

class OpenSearchService:
    def __init__(self):
        # Initialize OpenSearch client with basic auth
        self.client = OpenSearch(
            hosts=[{
                'host': settings.OPENSEARCH_HOST,
                'port': settings.OPENSEARCH_PORT
            }],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
            use_ssl=True,
            verify_certs=False,  # Set to True in production
            connection_class=RequestsHttpConnection,
            timeout=30
        )
        
        self.index_name = settings.OPENSEARCH_INDEX
        self._ensure_index()
    
    def _ensure_index(self):
        """Ensure the index exists with proper mapping"""
        if not self.client.indices.exists(self.index_name):
            mapping = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                },
                "mappings": {
                    "properties": {
                        "chunk_id": {"type": "keyword"},
                        "media_id": {"type": "keyword"},
                        "text": {"type": "text"},
                        "start_time": {"type": "float"},
                        "end_time": {"type": "float"},
                        "my_vector": {
                            "type": "knn_vector",
                            "dimension": 384,  # all-MiniLM-L6-v2 dimension
                            "method": {
                                "name": "hnsw",
                                "space_type": "l2",
                                "engine": "nmslib",
                                "parameters": {
                                    "ef_construction": 128,
                                    "m": 24
                                }
                            }
                        }
                    }
                }
            }
            
            self.client.indices.create(
                index=self.index_name,
                body=mapping
            )
    
    def index_chunk(self, chunk_id: int, media_id: int, text: str, 
                    start_time: float, end_time: float, vector: np.ndarray) -> Dict:
        """Index a single chunk with its embedding"""
        # Normalize the vector before indexing
        vector = vector / np.linalg.norm(vector)
        
        my_doc = {
            'id': f"{media_id}_{chunk_id}",
            'text': text,
            'my_vector': vector.tolist(),
            'chunk_id': str(chunk_id),
            'media_id': str(media_id),
            'start_time': start_time,
            'end_time': end_time
        }
        
        response = self.client.index(
            index=self.index_name,
            body=my_doc,
            id=my_doc['id'],
            refresh=True
        )
        return response
    
    def search_similar(
        self, 
        query_vector: np.ndarray,
        query_text: str,
        k: int = 1,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using k-NN search
        """
        # Normalize query vector
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        query = {
            "size": k,
            "query": {
                "knn": {
                    "my_vector": {
                        "vector": query_vector.tolist(),
                        "k": k
                    }
                }
            }
        }
        
        response = self.client.search(
            index=self.index_name,
            body=query
        )
        
        results = []
        for hit in response['hits']['hits']:
            # For k-NN with normalized vectors, score is cosine similarity
            # Already in -1 to 1 range, convert to 0 to 1
            score = (float(hit['_score']) + 1) / 2
            
            if score >= min_score:
                result = hit['_source']
                result['score'] = score
                results.append(result)
        
        # Sort by score in descending order
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def delete_by_media_id(self, media_id: int):
        """Delete all chunks for a specific media"""
        query = {
            "query": {
                "term": {
                    "media_id": str(media_id)
                }
            }
        }
        
        self.client.delete_by_query(
            index=self.index_name,
            body=query,
            refresh=True
        )

opensearch_service = OpenSearchService() 