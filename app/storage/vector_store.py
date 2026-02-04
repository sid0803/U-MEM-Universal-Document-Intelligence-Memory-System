import faiss
import numpy as np
import json
from pathlib import Path

# -----------------------------
# Config
# -----------------------------
DIM = 384
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

INDEX_FILE = DATA_DIR / "vectors.index"
META_FILE = DATA_DIR / "vector_metadata.json"

# -----------------------------
# Load / Init
# -----------------------------
if INDEX_FILE.exists():
    index = faiss.read_index(str(INDEX_FILE))
else:
    # Inner Product = Cosine similarity (for normalized vectors)
    index = faiss.IndexFlatIP(DIM)

if META_FILE.exists():
    metadata = json.loads(META_FILE.read_text())
else:
    metadata = []

# -----------------------------
# Add vector (chunk)
# -----------------------------
def add_document(embedding, meta: dict):
    if len(embedding) != DIM:
        raise ValueError(f"Embedding dimension mismatch: expected {DIM}, got {len(embedding)}")

    vector = np.array([embedding], dtype="float32")

    vector_id = index.ntotal  # FAISS id BEFORE adding
    index.add(vector)

    metadata.append({
        **meta,
        "vector_id": vector_id
    })

    # persist
    faiss.write_index(index, str(INDEX_FILE))
    META_FILE.write_text(json.dumps(metadata, indent=2))

    return vector_id

# -----------------------------
# Search similar (chunk-level)
# -----------------------------
def search_similar(embedding, k=5):
    if index.ntotal == 0:
        return []

    if len(embedding) != DIM:
        raise ValueError(f"Query embedding dimension mismatch: expected {DIM}, got {len(embedding)}")

    query = np.array([embedding], dtype="float32")
    scores, indices = index.search(query, k)

    results = []
    for pos, idx in enumerate(indices[0]):
        if idx == -1 or idx >= len(metadata):
            continue

        results.append({
            **metadata[idx],
            "score": float(scores[0][pos])  # higher = better
        })

    return results

def get_all_vectors():
    """
    Returns all vectors and metadata in index order.
    """
    vectors = index.reconstruct_n(0, index.ntotal)
    return vectors, metadata
