import requests
import os
import sys
from pathlib import Path
import time

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.services.opensearch_service import opensearch_service
from app.services.embedding import embedding_service
import pytest

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

def upload_video(file_path):
    """Upload a video file and return the response"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/media/upload", files=files)
    return response.json()

def search_content(query, k=10, min_score=0.6):
    """Search for content and return results"""
    response = requests.post(
        f"{BASE_URL}/query/search",
        params={
            "query": query,
            "k": k, 
            "min_score": min_score
        }
    )
    return response.json()

def delete_media(media_id):
    """Delete media and its associated data"""
    response = requests.delete(f"{BASE_URL}/media/{media_id}")
    return response.json()

def cleanup_test_data(media_id):
    """Clean up test data from both database and OpenSearch"""
    try:
        # Delete from database (which should also delete files)
        delete_media(media_id)
        # Delete from OpenSearch
        opensearch_service.delete_by_media_id(media_id)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")

def run_test():
    try:
        # Upload test video
        print("\nUploading video...")
        test_media_id = None
        upload_result = upload_video("uploads/crashcourse.mp4")
        print(f"Upload result: {upload_result}")
        
        if 'detail' in upload_result:
            raise Exception(f"Failed to upload: {upload_result['detail']}")
            
        test_media_id = upload_result['id']
        
        # Wait briefly for indexing
        time.sleep(2)
        
        # Test search
        print("\nSearching for: 'what is the link between consumption and genius'")
        results = search_content("what is the link between consumption and genius")
        print("\nRaw results:", results)
        
        print("\nResults:")
        if isinstance(results, list):  # Results should be a list of hits
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Text: {result.get('text', 'No text available')}")
                print(f"Time: {result.get('start_time', 0)}s to {result.get('end_time', 0)}s")
                print(f"Score: {result.get('score', 0)}")
                print(f"Media ID: {result.get('media_id', 'unknown')}")
        elif isinstance(results, dict) and 'detail' in results:
            print(f"Error in results: {results['detail']}")
        else:
            print(f"Unexpected results format: {results}")

    except Exception as e:
        print(f"Test error: {str(e)}")
        raise
    
    finally:
        # Clean up test data
        if test_media_id:
            print("\nCleaning up test data...")
            cleanup_test_data(test_media_id)
            print("Cleanup completed")

if __name__ == "__main__":
    run_test()
