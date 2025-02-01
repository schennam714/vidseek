import pytest
import time
from app.services.chunking import ChunkingService, Chunk

@pytest.fixture(scope="session")
def chunking_service():
    return ChunkingService(chunk_size=1600, overlap_size=337)  # Explicit overlap size

@pytest.fixture
def sample_transcript_segments():
    # Modified to have more semantically related content across segments
    return [
        ("Welcome to Our Grand Tour of Human Knowledge", 0.0, 15.5),
        ("The Renaissance period in Italy marked a dramatic cultural shift in European history, particularly in art and architecture.", 15.5, 45.2),
        ("Michelangelo's work on the Sistine Chapel ceiling took four years to complete, revolutionizing fresco painting techniques.", 45.2, 85.8),
        ("Meanwhile, in East Asia, the Ming Dynasty was experiencing its golden age of economic prosperity and cultural achievements.", 85.8, 125.3),
        ("The porcelain production techniques developed during this period remained unmatched for centuries.", 125.3, 165.7),
        ("Let's transition to modern physics", 165.7, 180.1),
        ("Quantum mechanics fundamentally changed our understanding of the microscopic world, introducing concepts like wave-particle duality.", 180.1, 228.4),
        ("The double-slit experiment demonstrated the strange behavior of particles at the quantum level.", 228.4, 268.9),
        ("String theory suggests the universe might have up to 11 dimensions, challenging our basic conception of reality.", 268.9, 315.6),
        ("Moving to environmental science", 315.6, 330.2),
        ("Coral reefs, often called the rainforests of the sea, are experiencing unprecedented levels of bleaching due to rising ocean temperatures.", 330.2, 380.7),
        ("Scientists estimate that over 50% of the Great Barrier Reef has been affected since 2016.", 380.7, 425.2),
        ("The interconnected nature of marine ecosystems means this damage has far-reaching consequences for global biodiversity.", 425.2, 475.8),
        ("Let's discuss culinary traditions", 475.8, 490.6),
        ("Traditional fermentation techniques have been used across cultures for thousands of years to preserve food.", 490.6, 538.3),
        ("From Korean kimchi to German sauerkraut, these methods not only extend shelf life but also create unique flavors and provide health benefits.", 538.3, 588.9),
        ("The biochemistry behind fermentation involves complex interactions between microorganisms and their environment.", 588.9, 635.4),
        ("Switching to space exploration", 635.4, 650.1),
        ("The James Webb Space Telescope has revolutionized our view of distant galaxies.", 650.1, 695.4),
        ("Its infrared capabilities allow us to observe celestial objects previously hidden from our view.", 695.4, 740.8),
        ("Recent observations have revealed potential signatures of water vapor in exoplanet atmospheres.", 740.8, 788.3),
        ("Let's explore ancient civilizations", 788.3, 803.5),
        ("The discovery of Göbekli Tepe in Turkey has challenged our understanding of prehistoric human societies.", 803.5, 855.2),
        ("This complex of circular structures predates agriculture, suggesting sophisticated organization before farming.", 855.2, 908.9),
        ("Moving to modern technology", 908.9, 923.5),
        ("Artificial Intelligence has made remarkable progress in natural language processing.", 923.5, 970.8),
        ("Large language models can now engage in sophisticated dialogue and assist in complex tasks.", 970.8, 1018.4),
        ("However, these systems still face challenges with contextual understanding and ethical decision-making.", 1018.4, 1065.9),
        ("Exploring neuroscience", 1065.9, 1080.2),
        ("Recent advances in brain-computer interfaces promise new hope for treating neurological conditions.", 1080.2, 1128.7),
        ("Scientists have successfully demonstrated direct neural control of prosthetic limbs.", 1128.7, 1175.3),
        ("The future of medicine", 1175.3, 1190.1),
        ("CRISPR gene editing technology is opening new frontiers in treating genetic diseases.", 1190.1, 1238.6),
        ("Clinical trials are showing promising results in conditions previously considered untreatable.", 1238.6, 1285.2),
        ("Understanding climate change", 1285.2, 1300.5),
        ("Global temperature records show an unprecedented rate of warming over the past century.", 1300.5, 1348.8),
        ("The Arctic is warming at nearly twice the global average rate.", 1348.8, 1395.4),
        ("Permafrost thaw could release significant amounts of stored carbon into the atmosphere.", 1395.4, 1442.9),
        ("The economics of renewable energy", 1442.9, 1458.3),
        ("Solar and wind power have become increasingly cost-competitive with fossil fuels.", 1458.3, 1505.7),
        ("Battery technology improvements are making renewable energy storage more viable.", 1505.7, 1552.4),
        ("The role of artificial intelligence in energy grid management", 1552.4, 1599.8),
        ("Mathematical discoveries", 1599.8, 1614.2),
        ("The Riemann Hypothesis remains one of mathematics' greatest unsolved problems.", 1614.2, 1661.5),
        ("Recent advances in prime number theory have opened new avenues in cryptography.", 1661.5, 1708.9),
        ("In conclusion", 1708.9, 1723.6),
        ("The interconnectedness of human knowledge spans across time, space, and disciplines.", 1723.6, 1760.5),
        ("Our journey through these diverse topics shows how each field contributes to our understanding of the world.", 1760.5, 1800.0)
    ]

def test_chunk_overlap(chunking_service, sample_transcript_segments):
    """Test that chunks properly overlap and preserve context"""
    chunks = chunking_service.create_chunks(sample_transcript_segments)
    
    print("\n=== Testing Chunk Overlap ===")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Text: {chunk.text}")
        print(f"Time: {chunk.start_time:.1f}s -> {chunk.end_time:.1f}s")
        print(f"Segment IDs: {chunk.segment_ids}")
        
        if i > 0:  # Check overlap with previous chunk
            prev_chunk = chunks[i-1]
            # Check if any segment IDs are shared between consecutive chunks
            overlap_segments = set(chunk.segment_ids) & set(prev_chunk.segment_ids)
            assert len(overlap_segments) > 0, f"No overlap found between chunks {i} and {i+1}"
            print(f"Overlaps with previous chunk through segments: {overlap_segments}")

def test_semantic_coherence(chunking_service):
    """Test that semantically related content stays together"""
    test_segments = [
        ("The quantum theory of physics deals with", 0.0, 10.0),
        ("microscopic phenomena at the atomic scale.", 10.0, 20.0),
        ("These quantum effects become important", 20.0, 30.0),
        ("when dealing with very small particles.", 30.0, 40.0),
        ("Classical physics, on the other hand,", 40.0, 50.0),
        ("describes macroscopic objects we see daily.", 50.0, 60.0)
    ]
    
    chunks = chunking_service.create_chunks(test_segments)
    
    print("\n=== Testing Semantic Coherence ===")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Text: {chunk.text}")
        print(f"Segment IDs: {chunk.segment_ids}")
        

def test_batch_processing(chunking_service):
    """Test that batch processing works correctly"""
    # Create a large number of segments with more content to ensure overlap
    large_segments = []
    for i in range(100):
        # Make segments longer to ensure overlap
        text = f"""This is segment {i} with content that should be properly chunked 
                  and maintain context across boundaries. Adding more text to ensure 
                  there is enough content for proper semantic chunking and overlap 
                  between segments. The quick brown fox jumps over the lazy dog 
                  while discussing important matters of great significance."""
        large_segments.append((
            text.replace('\n', ' ').replace('  ', ' '),
            float(i * 10),
            float((i + 1) * 10)
        ))
    
    start_time = time.time()
    chunks = chunking_service.create_chunks(large_segments)
    processing_time = time.time() - start_time
    
    print(f"\n=== Batch Processing Performance ===")
    print(f"Processed {len(large_segments)} segments into {len(chunks)} chunks")
    print(f"Processing time: {processing_time:.2f} seconds")
    

def test_parallel_processing(chunking_service, sample_transcript_segments):
    # Test with multiple batches
    start_time = time.time()
    chunks = chunking_service.create_chunks(sample_transcript_segments * 4)  # Multiply data
    end_time = time.time()
    
    print(f"\nProcessing time for {len(sample_transcript_segments * 4)} segments: {end_time - start_time:.2f}s")
    
    assert len(chunks) > 0

# Benchmarking tests
def test_performance(chunking_service, benchmark):
    # Create test data
    test_segments = []
    for i in range(200):  # Simulate 20 minutes of content
        test_segments.append((
            f"This is segment {i} with some additional text to make it more realistic and test the processing capabilities.",
            float(i * 6),
            float((i + 1) * 6)
        ))
    
    # Benchmark the chunking process
    def run_chunking():
        return chunking_service.create_chunks(test_segments)
    
    # Run benchmark and print results
    chunks = benchmark(run_chunking)
    print(f"\nProcessed {len(test_segments)} segments into {len(chunks)} chunks")
    print(f"Average chunk size: {sum(len(chunk.text) for chunk in chunks) / len(chunks):.0f} characters") 

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 