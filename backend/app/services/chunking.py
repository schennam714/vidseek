from typing import List, Tuple
from dataclasses import dataclass
import spacy

@dataclass
class Chunk:
    text: str
    start_time: float
    end_time: float
    segment_ids: List[int]

class ChunkingService:
    def __init__(self, target_chunk_size: int = 200, overlap_size: int = 5):
        self.nlp = spacy.load("en_core_web_sm")
        self.target_chunk_size = target_chunk_size
        self.overlap_size = overlap_size
    
    def create_chunks(self, segments: List[Tuple[str, float, float]]) -> List[Chunk]:
        if not segments:
            return []
        
        text_str = ""
        for i, (text, start, end) in enumerate(segments):
            text_str += text + " "
        # Step 1: Create semantic chunks based on sentence boundaries
        semantic_chunks = self._create_semantic_chunks(segments)
        
        # Step 2: Apply sliding window to each semantic chunk
        final_chunks = []
        for sem_chunk in semantic_chunks:
            sub_chunks = self._apply_sliding_window(sem_chunk)
            final_chunks.extend(sub_chunks)
        
        return final_chunks
    
    def _create_semantic_chunks(self, segments: List[Tuple[str, float, float]]) -> List[List[Tuple]]:
        # Step 1: Create full text while keeping track of segment boundaries
        full_text = ""
        char_to_segment_map = {}  # Maps character positions to segment indices
        current_char_pos = 0
        
        for i, (text, start, end) in enumerate(segments):
            # Map each character position to its segment index
            for _ in range(len(text) + 1):  # +1 for the space we'll add
                char_to_segment_map[current_char_pos] = i
                current_char_pos += 1
            full_text += text + " "
        
        # Step 2: Process with spaCy
        doc = self.nlp(full_text)
        
        # Step 3: Create chunks based on sentences while maintaining segment info
        chunks = []
        current_chunk = []
        current_text = ""
        
        for sent in doc.sents:
            # Find which segments this sentence spans
            start_char = sent.start_char
            end_char = sent.end_char
            start_segment = char_to_segment_map[start_char]
            end_segment = char_to_segment_map[min(end_char, len(full_text) - 1)]
            
            # Add all segments this sentence spans
            for seg_idx in range(start_segment, end_segment + 1):
                if segments[seg_idx] not in current_chunk:
                    current_chunk.append(segments[seg_idx])
            
            # Check if we should create a new chunk
            current_text = " ".join(seg[0] for seg in current_chunk)
            if len(current_text) > self.target_chunk_size:
                chunks.append(current_chunk)
                # Start new chunk with last segment for context
                current_chunk = [current_chunk[-1]] if current_chunk else []
                current_text = current_chunk[0][0] if current_chunk else ""
        
        # Add remaining segments
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _apply_sliding_window(self, segments: List[Tuple[str, float, float]]) -> List[Chunk]:
        chunks = []
        start_idx = 0
        
        while start_idx < len(segments):
            current_duration = 0
            end_idx = start_idx
            
            # Build chunk up to target size
            while (end_idx < len(segments) and 
                   current_duration < self.target_chunk_size):
                _, _, end_time = segments[end_idx]
                _, start_time, _ = segments[start_idx]
                current_duration = end_time - start_time
                end_idx += 1
            
            # Create chunk
            chunk_segments = segments[start_idx:end_idx]
            if chunk_segments:
                chunks.append(Chunk(
                    text=" ".join(seg[0] for seg in chunk_segments),
                    start_time=chunk_segments[0][1],
                    end_time=chunk_segments[-1][2],
                    segment_ids=list(range(start_idx, end_idx))
                ))
            
            # Move window forward (with overlap)
            time_to_move = self.target_chunk_size - self.overlap_size
            while (start_idx < len(segments) and 
                   segments[start_idx][2] - segments[0][1] < time_to_move):
                start_idx += 1
        
        return chunks 