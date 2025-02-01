import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

def upload_video(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/media/upload", files=files)
    return response.json()

def search_content(query, k=10, min_score=0.7):
    response = requests.post(
        f"{BASE_URL}/query/search",
        params={"k": k, "min_score": min_score},
        json={"query": query}
    )
    return response.json()

# Test sequence
def run_test():
    # 1. Upload video
    print("Uploading video...")
    result = upload_video("path/to/your/video.mp4")
    print(f"Upload result: {result}\n")

    # 2. Try different searches
    test_queries = [
        "introduction to the topic",
        "main points discussed",
        "conclusion of the presentation"
    ]

    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = search_content(query)
        print("\nResults:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Text: {result['text']}")
            print(f"Time: {result['start_time']}s to {result['end_time']}s")
            print(f"Score: {result['score']}")
            print(f"Media ID: {result['media_id']}")

if __name__ == "__main__":
    run_test()
