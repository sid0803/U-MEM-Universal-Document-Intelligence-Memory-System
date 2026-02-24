from functools import lru_cache
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import EMBEDDING_MODEL, VECTOR_DIM


# -----------------------------
# Model Loader (cached)
# -----------------------------
@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """
    Load and cache the embedding model.
    """
    return SentenceTransformer(EMBEDDING_MODEL)


# -----------------------------
# Internal Normalization Helper
# -----------------------------
def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


# -----------------------------
# Embed Single Text
# -----------------------------
def embed_text(text: str) -> List[float]:
    """
    Generate a normalized embedding for a single text input.
    """
    if not isinstance(text, str):
        raise TypeError("embed_text expects a string")

    if not text.strip():
        return [0.0] * VECTOR_DIM

    model = get_model()

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=False
    )

    embedding = np.asarray(embedding)

    if embedding.shape[0] != VECTOR_DIM:
        raise ValueError(
            f"Embedding dimension mismatch: expected {VECTOR_DIM}, got {embedding.shape[0]}"
        )

    embedding = _normalize(embedding)

    return embedding.tolist()


# -----------------------------
# Embed Multiple Texts (Batch)
# -----------------------------
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate normalized embeddings for multiple texts.
    """
    if not isinstance(texts, list):
        raise TypeError("embed_texts expects a list of strings")

    if not texts:
        return []

    model = get_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=False,
        batch_size=32
    )

    embeddings = np.asarray(embeddings)

    if embeddings.shape[1] != VECTOR_DIM:
        raise ValueError(
            f"Embedding dimension mismatch: expected {VECTOR_DIM}, got {embeddings.shape[1]}"
        )

    normalized = np.array([_normalize(vec) for vec in embeddings])

    return normalized.tolist()
