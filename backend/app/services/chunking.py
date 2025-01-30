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
        
        # Get semantic chunks (each chunk is a list of (text, start, end) tuples)
        semantic_chunks = self._create_semantic_chunks(segments)
        
        # Convert semantic chunks to Chunk objects
        final_chunks = []
        for i, segment_group in enumerate(semantic_chunks):
            final_chunks.append(Chunk(
                text=" ".join(seg[0] for seg in segment_group),
                start_time=segment_group[0][1],  # First segment's start time
                end_time=segment_group[-1][2],   # Last segment's end time
                # Find the indices of these segments in the original list
                segment_ids=[segments.index(seg) for seg in segment_group]
            ))
        
        return final_chunks
    
    def _create_semantic_chunks(self, segments: List[Tuple[str, float, float]]) -> List[List[Tuple]]:
        # Step 1: Create full text while keeping track of segment boundaries
        full_text = ""
        char_to_segment_map = {}
        current_char_pos = 0
        
        for i, (text, start, end) in enumerate(segments):
            for _ in range(len(text) + 1):
                char_to_segment_map[current_char_pos] = i
                current_char_pos += 1
            full_text += text + " "
        
        # Step 2: Process with spaCy
        doc = self.nlp(full_text)
        
        # Step 3: Create chunks based on sentences
        chunks = []
        current_chunk = []
        used_segments = set()  # Track which segments we've used
        
        for sent in doc.sents:
            start_char = sent.start_char
            end_char = sent.end_char
            start_segment = char_to_segment_map[start_char]
            end_segment = char_to_segment_map[min(end_char, len(full_text) - 1)]
            
            # Get segments for this sentence
            sentence_segments = []
            for i in range(start_segment, end_segment + 1):
                if i not in used_segments:  # Only use segments we haven't used yet
                    sentence_segments.append(segments[i])
                    used_segments.add(i)
            
            if not sentence_segments:
                continue
            
            # Check if we can add to current chunk
            if current_chunk:
                if current_chunk[-1][2] == sentence_segments[0][1]:
                    current_chunk.extend(sentence_segments)
                else:
                    # Start new chunk
                    chunks.append(current_chunk)
                    current_chunk = sentence_segments
            else:
                current_chunk = sentence_segments
            
            # Check size limit
            if len(" ".join(seg[0] for seg in current_chunk)) > self.target_chunk_size:
                chunks.append(current_chunk)
                current_chunk = []
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # Sort chunks by start time to ensure chronological order
        chunks.sort(key=lambda chunk: chunk[0][1])
        
        return chunks