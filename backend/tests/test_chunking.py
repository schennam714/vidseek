import pytest
from app.services.chunking import ChunkingService, Chunk

@pytest.fixture(scope="session")
def chunking_service():
    return ChunkingService(target_chunk_size=200, overlap_size=2)  # Smaller sizes for testing

@pytest.fixture
def sample_transcript_segments():
    return [
        ("Introduction", 0.0, 3.0),
        ("Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data.", 3.0, 15.5),
        ("It draws from statistics, computer science, machine learning, and various data analysis techniques to discover patterns, make predictions, and derive actionable insights.", 15.5, 28.0),
        ("Data Science can be applied across many industries, including healthcare, finance, marketing, and education, where it helps organizations make data-driven decisions, optimize processes, and understand customer behaviors.", 28.0, 43.0),
        ("Overview of Big Data", 43.0, 46.0),
        ("Big data refers to large, diverse sets of information that grow at ever-increasing rates.", 46.0, 54.0),
        ("It encompasses the volume of information, the velocity or speed at which it is created and collected, and the variety or scope of the data points being covered.", 54.0, 66.0),
        ("Data Science Methods", 66.0, 69.0),
        ("There are several important methods used in Data Science:", 69.0, 74.0),
        ("1. Regression Analysis 2. Classification 3. Clustering 4. Neural Networks", 74.0, 82.0),
        ("Challenges in Data Science", 82.0, 85.0),
        ("Data Quality: Poor data quality can lead to incorrect conclusions.", 85.0, 91.0),
        ("Data Privacy: Ensuring the privacy of sensitive information.", 91.0, 96.0),
        ("Scalability: Handling massive datasets efficiently.", 96.0, 101.0),
        ("Conclusion", 101.0, 103.0),
        ("Data Science continues to be a driving force in many industries, offering insights that can lead to better decisions and optimized outcomes.", 103.0, 114.0),
        ("It remains an evolving field that incorporates the latest technological advancements.", 114.0, 122.0)
    ]


def test_semantic_chunking(chunking_service, sample_transcript_segments):
    chunks = chunking_service._create_semantic_chunks(sample_transcript_segments)
    
    # Print chunks for debugging
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i}:")
        for text, start, end in chunk:
            print(f"  {start:.1f} -> {end:.1f}: {text}")
    
    # Verify basic chunking
    assert len(chunks) > 0
    
    # Verify timestamp continuity within chunks
    for chunk in chunks:
        for i in range(len(chunk) - 1):
            # End time of current segment should match start time of next
            assert chunk[i][2] == chunk[i + 1][1]
    
    # Verify content
    first_chunk = chunks[0]
    assert first_chunk[0][1] == sample_transcript_segments[0][1]  # Check timestamp preservation

# def test_sliding_window(chunking_service):
#     segment_chunk = [
#         ("First segment", 0.0, 4.0),
#         ("Second segment", 4.0, 8.0),
#         ("Third segment", 8.0, 12.0)
#     ]
    
#     chunks = chunking_service._apply_sliding_window(segment_chunk)
    
#     # With target_size=10 and overlap=2, should create overlapping chunks
#     assert len(chunks) >= 2
#     assert chunks[0].start_time == 0.0
#     assert chunks[-1].end_time == 12.0
    
#     # Check overlap
#     for i in range(len(chunks) - 1):
#         assert chunks[i].end_time > chunks[i + 1].start_time

# def test_empty_input(chunking_service):
#     chunks = chunking_service.create_chunks([])
#     assert chunks == []

# def test_single_segment(chunking_service):
#     segments = [("This is a test.", 0.0, 3.0)]
#     chunks = chunking_service.create_chunks(segments)
#     assert len(chunks) == 1
#     assert chunks[0].text == "This is a test."
#     assert chunks[0].start_time == 0.0
#     assert chunks[0].end_time == 3.0
#     assert chunks[0].segment_ids == [0]

# def test_time_based_chunking(chunking_service):
#     # Test that chunks respect time boundaries
#     segments = [
#         ("Part one.", 0.0, 5.0),
#         ("Part two.", 5.0, 10.0),
#         ("Part three.", 10.0, 15.0)
#     ]
    
#     chunks = chunking_service.create_chunks(segments)
    
#     # With target_size=10, should split into 2 chunks with overlap
#     assert len(chunks) == 2
#     # First chunk should be ~10 seconds
#     assert chunks[0].end_time - chunks[0].start_time <= 10
#     # Should have overlap
#     assert chunks[0].end_time > chunks[1].start_time

# def test_segment_ids_continuity(chunking_service):
#     segments = [
#         ("One.", 0.0, 3.0),
#         ("Two.", 3.0, 6.0),
#         ("Three.", 6.0, 9.0),
#         ("Four.", 9.0, 12.0)
#     ]
    
#     chunks = chunking_service.create_chunks(segments)
    
#     # Check that segment IDs are continuous and valid
#     for chunk in chunks:
#         # IDs should be sequential
#         assert chunk.segment_ids == list(range(min(chunk.segment_ids), max(chunk.segment_ids) + 1))
#         # IDs should be within valid range
#         assert all(0 <= id < len(segments) for id in chunk.segment_ids) 