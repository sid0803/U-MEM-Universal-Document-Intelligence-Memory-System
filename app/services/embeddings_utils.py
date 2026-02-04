import numpy as np

EMBEDDING_DIM = 384

def normalize_embedding(vec):
    if vec is None or len(vec) != EMBEDDING_DIM:
        # fail-safe: return zero vector
        return [0.0] * EMBEDDING_DIM

    v = np.array(vec, dtype="float32")
    norm = np.linalg.norm(v)

    if norm == 0.0:
        return v.tolist()

    return (v / norm).tolist()
