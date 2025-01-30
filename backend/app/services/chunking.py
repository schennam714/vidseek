from typing import List, Tuple
from dataclasses import dataclass
import spacy
from concurrent.futures import ThreadPoolExecutor

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
                if batch_chunks:  # Only extend if we got results
                    all_chunks.extend(batch_chunks)
        
        # Convert to final Chunk objects
        return [
            Chunk(
                text=" ".join(seg[0] for seg in chunk),
                start_time=chunk[0][1],
                end_time=chunk[-1][2],
                segment_ids=[segments.index(seg) for seg in chunk]
            )
            for chunk in all_chunks
        ]
    
    def _process_batch(self, segments: List[Tuple[str, float, float]], offset: int) -> List[List[Tuple]]:
        # Create full text for spaCy
        full_text = ""
        char_to_segment_map = {}
        current_char_pos = 0
        
        for i, (text, _, _) in enumerate(segments):
            for _ in range(len(text) + 1):
                char_to_segment_map[current_char_pos] = i
                current_char_pos += 1
            full_text += text + " "
        
        # Process with spaCy
        doc = self.nlp(full_text)
        
        # Create chunks
        chunks = []
        current_chunk = []
        used_segments = set()
        
        for sent in doc.sents:
            start_char = sent.start_char
            end_char = sent.end_char
            start_segment = char_to_segment_map[start_char]
            end_segment = char_to_segment_map[min(end_char, len(full_text) - 1)]
            
            # Get segments for this sentence
            sentence_segments = []
            for i in range(start_segment, end_segment + 1):
                if i not in used_segments:
                    sentence_segments.append(segments[i])
                    used_segments.add(i)
            
            if not sentence_segments:
                continue
            
            # Check if we can add to current chunk
            if current_chunk:
                if current_chunk[-1][2] == sentence_segments[0][1]:
                    current_chunk.extend(sentence_segments)
                else:
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
        
        return chunks