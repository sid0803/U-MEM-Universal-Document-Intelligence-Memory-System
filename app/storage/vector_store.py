import faiss
import numpy as np
import json
import threading
import logging
from pathlib import Path
from app.core.config import VECTOR_DIM

logger = logging.getLogger(__name__)

# ==========================================================
# Config
# ==========================================================
DIM = VECTOR_DIM

VECTORS_DIR = Path("data/vectors")
VECTORS_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = VECTORS_DIR / "faiss.index"
META_FILE = VECTORS_DIR / "vector_metadata.json"

_lock = threading.Lock()


# ==========================================================
# Safe JSON Load
# ==========================================================
def _safe_load_metadata():
    if not META_FILE.exists():
        return []

    try:
        content = META_FILE.read_text().strip()
        if not content:
            return []

        data = json.loads(content)

        if not isinstance(data, list):
            raise ValueError("Metadata must be list")

        return data

    except Exception as e:
        logger.error("Corrupted vector metadata. Resetting. Error: %s", e)
        META_FILE.unlink(missing_ok=True)
        return []


# ==========================================================
# Initialize Index + Metadata
# ==========================================================
def _initialize_index():
    if INDEX_FILE.exists():
        try:
            return faiss.read_index(str(INDEX_FILE))
        except Exception as e:
            logger.error("Failed to load FAISS index. Resetting. Error: %s", e)

    return faiss.IndexFlatIP(DIM)


index = _initialize_index()
metadata = _safe_load_metadata()


# ==========================================================
# Consistency Check (Safe)
# ==========================================================
def _validate_consistency():
    if index.ntotal != len(metadata):
        logger.warning(
            "Vector index mismatch detected. Resetting index safely."
        )
        index.reset()
        metadata.clear()
        _persist()


_validate_consistency()


# ==========================================================
# Atomic Persist
# ==========================================================
def _persist():
    tmp_index = INDEX_FILE.with_suffix(".tmp")
    tmp_meta = META_FILE.with_suffix(".tmp")

    faiss.write_index(index, str(tmp_index))
    tmp_meta.write_text(json.dumps(metadata, indent=2))

    tmp_index.replace(INDEX_FILE)
    tmp_meta.replace(META_FILE)


# ==========================================================
# Add Vectors
# ==========================================================
def add_vectors(doc_id: str, chunks: list, embeddings: list, user_id: str):
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings length mismatch")

    with _lock:
        for chunk, embedding in zip(chunks, embeddings):
            _add_single_vector(chunk, embedding, doc_id, user_id)

        _persist()


def _add_single_vector(chunk: dict, embedding, doc_id: str, user_id: str):
    if embedding is None:
        raise ValueError("Embedding cannot be None")

    if len(embedding) != DIM:
        raise ValueError(
            f"Embedding dimension mismatch: expected {DIM}, got {len(embedding)}"
        )

    vector = np.asarray([embedding], dtype="float32")

    vector_id = index.ntotal
    index.add(vector)

    metadata.append({
        "vector_id": vector_id,
        "chunk_id": chunk["chunk_id"],
        "doc_id": doc_id,
        "user_id": user_id,
    })


# ==========================================================
# Search (User Scoped)
# ==========================================================
def search_similar(embedding, k=5, user_id: str | None = None):
    if not user_id:
        raise ValueError("user_id is required")

    if index.ntotal == 0:
        return []

    if embedding is None:
        raise ValueError("Query embedding cannot be None")

    if len(embedding) != DIM:
        raise ValueError(
            f"Query embedding dimension mismatch: expected {DIM}, got {len(embedding)}"
        )

    query = np.asarray([embedding], dtype="float32")

    search_k = min(index.ntotal, k * 3)
    scores, indices = index.search(query, search_k)

    results = []

    for pos, idx in enumerate(indices[0]):
        if idx == -1 or idx >= len(metadata):
            continue

        meta = metadata[idx]

        if meta["user_id"] != user_id:
            continue

        results.append({
            **meta,
            "score": float(scores[0][pos]),
        })

        if len(results) >= k:
            break

    return results


# ==========================================================
# Get All Vectors (User Scoped)
# ==========================================================
def get_all_vectors(user_id: str):
    if not user_id:
        raise ValueError("user_id is required")

    if index.ntotal == 0:
        return [], []

    user_vectors = []
    user_meta = []

    for i, meta in enumerate(metadata):
        if meta["user_id"] != user_id:
            continue

        try:
            vector = index.reconstruct(i)
        except Exception as e:
            logger.error("Vector reconstruction failed: %s", e)
            continue

        user_vectors.append(vector.tolist())
        user_meta.append(meta)

    return user_vectors, user_meta


# ==========================================================
# Reset (Testing Utility)
# ==========================================================
def reset_store():
    """
    For testing only.
    Clears index + metadata safely.
    """
    global index, metadata

    with _lock:
        index = faiss.IndexFlatIP(DIM)
        metadata = []
        _persist()
