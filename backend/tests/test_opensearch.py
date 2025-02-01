from app.services.opensearch_service import opensearch_service
from app.services.embedding import embedding_service
from opensearchpy.exceptions import OpenSearchException
import numpy as np

def test_opensearch_connection():
    try:
        # Check if we can connect and get cluster health
        health = opensearch_service.client.cluster.health()
        print("\nCluster Health:")
        print(f"Status: {health['status']}")
        print(f"Number of nodes: {health['number_of_nodes']}")
            
        return True
        
    except OpenSearchException as e:
        print(f"\nOpenSearch Connection Error: {str(e)}")
        return False
    except Exception as e:
        print(f"\nConnection Error: {str(e)}")
        return False

def test_index_and_search():
    try:
        print("\nSetting up test index...")
        # Force delete the index if it exists
        if opensearch_service.client.indices.exists(opensearch_service.index_name):
            print("Deleting existing index...")
            opensearch_service.client.indices.delete(opensearch_service.index_name)
        
        # Create mapping
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
        
        # Create index with mapping
        print("Creating new index with k-NN mapping...")
        opensearch_service.client.indices.create(
            index=opensearch_service.index_name,
            body=mapping
        )
        
        # Test data - multiple chunks
        test_chunks = [
            {
                "chunk_id": 1,
                "media_id": 999,
                "text": "Machine learning is a subset of artificial intelligence that focuses on data and algorithms",
                "start_time": 0.0,
                "end_time": 10.0
            },
            {
                "chunk_id": 2,
                "media_id": 999,
                "text": "Deep neural networks are used in modern AI applications for complex tasks",
                "start_time": 10.0,
                "end_time": 20.0
            },
            {
                "chunk_id": 3,
                "media_id": 999,
                "text": "Natural language processing enables computers to understand human language",
                "start_time": 20.0,
                "end_time": 30.0
            },
            {
                "chunk_id": 4,
                "media_id": 999,
                "text": "Computer vision systems can detect and classify objects in images and video",
                "start_time": 30.0,
                "end_time": 40.0
            },
            {
                "chunk_id": 5,
                "media_id": 999,
                "text": "The best way to make pasta is to boil it in salted water until al dente",
                "start_time": 40.0,
                "end_time": 50.0
            },
            {
                "chunk_id": 6,
                "media_id": 999,
                "text": "A good tomato sauce starts with quality ingredients and proper seasoning",
                "start_time": 50.0,
                "end_time": 60.0
            },
            {
                "chunk_id": 7,
                "media_id": 999,
                "text": "Reinforcement learning allows AI agents to learn through trial and error",
                "start_time": 60.0,
                "end_time": 70.0
            },
            {
                "chunk_id": 8,
                "media_id": 999,
                "text": "Transfer learning enables models to apply knowledge from one task to another",
                "start_time": 70.0,
                "end_time": 80.0
            },
            {
                "chunk_id": 9,
                "media_id": 999,
                "text": "The perfect pizza requires a hot oven and well-kneaded dough",
                "start_time": 80.0,
                "end_time": 90.0
            },
            {
                "chunk_id": 10,
                "media_id": 999,
                "text": "Data preprocessing is crucial for training effective machine learning models",
                "start_time": 90.0,
                "end_time": 100.0
            },
            {
                "chunk_id": 11,
                "media_id": 999,
                "text": "Feature engineering helps improve model performance by creating meaningful inputs",
                "start_time": 100.0,
                "end_time": 110.0
            },
            {
                "chunk_id": 12,
                "media_id": 999,
                "text": "Baking bread requires patience and attention to temperature and timing",
                "start_time": 110.0,
                "end_time": 120.0
            }
        ]
        
        print("\nIndexing test chunks...")
        for chunk in test_chunks:
            # Generate embedding
            vector = embedding_service.generate_embedding(chunk["text"])
            
            # Index the chunk
            response = opensearch_service.index_chunk(
                chunk_id=chunk["chunk_id"],
                media_id=chunk["media_id"],
                text=chunk["text"],
                start_time=chunk["start_time"],
                end_time=chunk["end_time"],
                vector=vector
            )
            print(f"Indexed chunk {chunk['chunk_id']}: {response['result']}")

        # Test search with different queries
        test_queries = [
            ("Tell me about machine learning", ["1", "2", "7", "10", "11"]),  # ML related
            ("How to cook pasta and sauce", ["5", "6"]),  # Cooking related
            ("What is deep learning", ["2", "7", "8"]),  # AI/Deep learning
            ("Cooking and baking", ["5", "6", "9", "12"]),  # Food related
            ("quantum computing", [])  # Should match nothing with high score
        ]

        for query, expected_chunks in test_queries:
            print(f"\nSearching for: '{query}'")
            query_vector = embedding_service.generate_embedding(query)
            results = opensearch_service.search_similar(
                query_vector=query_vector,
                query_text=query,
                k=3,  # Get top 3 results
                min_score=0.6  # Higher threshold for better precision
            )
            
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Text: {result['text']}")
                print(f"Score: {result['score']:.3f}")
                print(f"Time: {result['start_time']}s to {result['end_time']}s")

            # Verify that results are semantically relevant
            if query == "Tell me about machine learning":
                assert any("machine learning" in r['text'].lower() or "ai" in r['text'].lower() 
                          for r in results), "Expected ML/AI related results"
            elif query == "How to cook pasta and sauce":
                assert any("pasta" in r['text'].lower() for r in results), "Expected cooking related results"

        return True

    except Exception as e:
        print(f"\nTest Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenSearch Setup...")
    
    print("\n1. Testing Connection...")
    if not test_opensearch_connection():
        print("Connection test failed! Stopping further tests.")
        exit(1)
    
    print("\n2. Testing Index and Search...")
    test_index_and_search()

