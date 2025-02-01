from typing import List, Tuple, Dict
from dataclasses import dataclass
import spacy
from concurrent.futures import ThreadPoolExecutor
from langchain.text_splitter import MarkdownTextSplitter

@dataclass
class Chunk:
    text: str
    start_time: float
    end_time: float
    segment_ids: List[int]

class ChunkingService:
    def __init__(self, chunk_size: int = 1600, overlap_size: int = 337):
        """Initialize the chunking service with configurable chunk and overlap sizes"""
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.text_splitter = MarkdownTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size
        )
    
    def create_chunks(self, segments: List[Tuple[str, float, float]]) -> List[Chunk]:
        """Create overlapping chunks while preserving timing information"""
        if not segments:
            return []
        
        # Process in parallel batches
        BATCH_SIZE = 50
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(0, len(segments), BATCH_SIZE):
                batch = segments[i:min(i + BATCH_SIZE, len(segments))]
                futures.append(executor.submit(self._process_batch, batch, i))
            
            all_chunks = []
            for future in futures:
                batch_chunks = future.result()
                if batch_chunks:
                    all_chunks.extend(batch_chunks)
        
        return all_chunks

    def _process_batch(self, segments: List[Tuple[str, float, float]], offset: int) -> List[Chunk]:
        """Process a batch of segments using LangChain's text splitter"""
        # First, combine all segment texts while keeping track of their boundaries
        combined_text = ""
        segment_boundaries = []
        current_pos = 0
        
        for i, segment in enumerate(segments):
            text, start_time, end_time = segment  # Unpack tuple
            segment_boundaries.append({
                'start_pos': current_pos,
                'end_pos': current_pos + len(text),
                'segment_idx': offset + i,
                'start_time': start_time,
                'end_time': end_time
            })
            combined_text += text + " "  # Add space between segments
            current_pos += len(text) + 1  # +1 for the space
        
        # Use LangChain to split the text
        split_texts = self.text_splitter.split_text(combined_text)
        
        chunks = []
        for text in split_texts:
            # Find which segments this chunk overlaps with
            chunk_start = combined_text.find(text)
            chunk_end = chunk_start + len(text)
            
            # Find overlapping segments
            overlapping_segments = []
            chunk_start_time = None
            chunk_end_time = None
            
            for boundary in segment_boundaries:
                if (chunk_start <= boundary['end_pos'] and 
                    chunk_end >= boundary['start_pos']):
                    overlapping_segments.append(boundary['segment_idx'])
                    if chunk_start_time is None:
                        chunk_start_time = boundary['start_time']
                    chunk_end_time = boundary['end_time']
            
            if overlapping_segments:
                chunks.append(Chunk(
                    text=text.strip(),
                    start_time=chunk_start_time,
                    end_time=chunk_end_time,
                    segment_ids=overlapping_segments
                ))
        
        return chunks