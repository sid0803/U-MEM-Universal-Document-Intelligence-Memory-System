from sentence_transformers import SentenceTransformer
from functools import lru_cache
from app.services.embeddings_utils import normalize_embedding

@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list:
    if not text or not text.strip():
        return [0.0] * 384

    model = get_model()

    # Always return numpy array
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=False
    )

    # Normalize → returns list
    return normalize_embedding(embedding)
