import uuid
from typing import List

def chunk_text(
    text: str,
    max_tokens: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Simple word-based chunking.
    Later you can replace this with tokenizer-based chunking.
    """
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + max_tokens
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)

        start = end - overlap

    return chunks
