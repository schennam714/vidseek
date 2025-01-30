import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.chunking import ChunkingService

def generate_test_data(duration_minutes: int = 60) -> list:
    """Generate test data for a specified duration"""
    segments = []
    segments_per_minute = 10
    total_segments = duration_minutes * segments_per_minute
    
    for i in range(total_segments):
        segments.append((
            f"This is segment {i} of the test transcript. It contains enough text "
            f"to make it realistic for testing purposes. Adding more content to "
            f"simulate actual transcription output.",
            float(i * 6),
            float((i + 1) * 6)
        ))
    return segments

def benchmark_chunking(duration_minutes: int = 60):
    """Benchmark chunking performance for different video lengths"""
    service = ChunkingService()
    segments = generate_test_data(duration_minutes)
    
    print(f"\nBenchmarking with {duration_minutes} minutes of content "
          f"({len(segments)} segments):")
    
    # Warm-up run
    _ = service.create_chunks(segments[:50])
    
    # Actual benchmark
    start_time = time.time()
    chunks = service.create_chunks(segments)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Chunks created: {len(chunks)}")
    print(f"Processing speed: {duration_minutes/processing_time:.2f}x realtime")
    
    return processing_time, len(chunks)

if __name__ == "__main__":
    durations = [5, 15, 30, 60]
    results = []
    
    print("Running chunking benchmarks...")
    for duration in durations:
        time_taken, num_chunks = benchmark_chunking(duration)
        results.append((duration, time_taken, num_chunks))
    
    print("\nSummary:")
    print("Duration (min) | Processing Time (s) | Chunks | Speed (x realtime)")
    print("-" * 65)
    for duration, time_taken, chunks in results:
        print(f"{duration:13d} | {time_taken:16.2f} | {chunks:6d} | {duration*60/time_taken:17.2f}x") 