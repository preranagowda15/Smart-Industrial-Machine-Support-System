"""
Text chunking service for manufacturing manuals.
Splits text into meaningful passages (700-1000 chars, 100-150 overlap)
preferring sentence/paragraph boundaries and preserving complete source metadata.
"""
import hashlib
from typing import List, Dict, Any

class ChunkingService:
    def __init__(self, chunk_size: int = 850, overlap: int = 120):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits single page text into overlapping chunks, respecting
        paragraph breaks and sentence boundaries where possible.
        """
        text = text.strip()
        if not text:
            return []
        
        # If the page text fits comfortably in a single chunk, return it directly
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        total_len = len(text)

        while start < total_len:
            end = min(total_len, start + self.chunk_size)
            if end < total_len:
                # Look for paragraph break
                para_break = text.rfind("\n\n", start, end)
                if para_break != -1 and para_break > start + (self.chunk_size // 2):
                    end = para_break + 2
                else:
                    # Look for sentence boundary
                    sentence_end = -1
                    for punct in [". ", "? ", "! ", ".\n"]:
                        p = text.rfind(punct, start, end)
                        if p > sentence_end and p > start + (self.chunk_size // 2):
                            sentence_end = p + len(punct)
                    if sentence_end != -1:
                        end = sentence_end
                    else:
                        # Fallback to word boundary
                        space = text.rfind(" ", start, end)
                        if space != -1 and space > start + (self.chunk_size // 2):
                            end = space + 1

            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(chunk_content)

            if end >= total_len:
                break
            
            # Slide start forward with overlap
            next_start = end - self.overlap
            if next_start <= start:
                next_start = start + 1
            start = next_start

        return chunks

    def process_pages(
        self,
        pages: List[Dict[str, Any]],
        machine_code: str,
        document_name: str,
        revision: str,
        manual_id: Any = None,
        filename: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Processes a list of extracted pages into indexed chunk dictionaries with stable IDs.
        """
        chunk_records = []
        global_chunk_idx = 0

        for page in pages:
            page_no = page["page_number"]
            page_text = page["text"]
            pieces = self.split_text(page_text)

            for chunk_idx, piece in enumerate(pieces):
                # Deterministic stable chunk ID
                raw_id_key = f"{machine_code}|{document_name}|{revision}|p{page_no}|c{chunk_idx}"
                embedding_id = hashlib.sha256(raw_id_key.encode("utf-8")).hexdigest()

                chunk_records.append({
                    "embedding_id": embedding_id,
                    "machine_code": machine_code,
                    "document_name": document_name,
                    "revision": revision,
                    "page_number": page_no,
                    "chunk_index": chunk_idx,
                    "global_index": global_chunk_idx,
                    "chunk_text": piece,
                    "manual_id": manual_id,
                    "filename": filename,
                })
                global_chunk_idx += 1

        return chunk_records

