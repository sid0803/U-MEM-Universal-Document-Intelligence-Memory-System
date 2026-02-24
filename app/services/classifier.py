from functools import lru_cache
from typing import Dict

from app.services.embeddings import embed_text
from app.services.similarity import cosine_similarity


# -------------------------
# Definitions
# -------------------------

DOCUMENT_TYPE_DEFINITIONS = {
    "Resume": "resume cv experience skills education work history projects certifications",
    "Research_Paper": "abstract introduction methodology results conclusion references",
    "Invoice": "invoice gst billing total amount payment",
    "Notes": "notes explanation summary learning concepts",
}

SUBJECT_DEFINITIONS = {
    "AI": "machine learning deep learning neural networks nlp computer vision",
    "Database": "sql database indexing normalization transactions",
    "Finance": "tax gst revenue profit loss accounting",
    "General": "general document miscellaneous",
}


# -------------------------
# Lazy Reference Vector Loader
# -------------------------

@lru_cache(maxsize=1)
def get_document_type_vectors() -> Dict[str, list]:
    return {
        label: embed_text(desc)
        for label, desc in DOCUMENT_TYPE_DEFINITIONS.items()
    }


@lru_cache(maxsize=1)
def get_subject_vectors() -> Dict[str, list]:
    return {
        label: embed_text(desc)
        for label, desc in SUBJECT_DEFINITIONS.items()
    }


# -------------------------
# Core Classification Logic
# -------------------------

def classify_by_embedding(text: str, reference_vectors: Dict[str, list]) -> str:
    if not text or not text.strip():
        return "General"

    text_vector = embed_text(text)

    best_label = "General"
    best_score = -1.0

    for label, ref_vector in reference_vectors.items():
        score = cosine_similarity(text_vector, ref_vector)
        if score > best_score:
            best_score = score
            best_label = label

    return best_label


def classify_document_type(text: str) -> str:
    vectors = get_document_type_vectors()
    return classify_by_embedding(text, vectors)


def classify_subject(text: str, document_type: str) -> str:
    # Guard: Resumes should not get subject classification
    if document_type == "Resume":
        return "General"

    vectors = get_subject_vectors()
    return classify_by_embedding(text, vectors)
