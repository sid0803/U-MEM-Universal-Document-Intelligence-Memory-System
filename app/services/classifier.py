from app.services.embeddings import embed_text
from app.services.similarity import cosine_similarity

DOCUMENT_TYPE_DEFINITIONS = {
    "Resume": "resume cv experience skills education work history projects certifications",
    "Research_Paper": "abstract introduction methodology results conclusion references",
    "Invoice": "invoice gst billing total amount payment",
    "Notes": "notes explanation summary learning concepts"
}

SUBJECT_DEFINITIONS = {
    "AI": "machine learning deep learning neural networks nlp computer vision",
    "Database": "sql database indexing normalization transactions",
    "Finance": "tax gst revenue profit loss accounting",
    "General": "general document miscellaneous"
}

DOCUMENT_TYPE_VECTORS = {
    label: embed_text(desc)
    for label, desc in DOCUMENT_TYPE_DEFINITIONS.items()
}

SUBJECT_VECTORS = {
    label: embed_text(desc)
    for label, desc in SUBJECT_DEFINITIONS.items()
}


def classify_by_embedding(text: str, reference_vectors: dict) -> str:
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
    return classify_by_embedding(text, DOCUMENT_TYPE_VECTORS)


def classify_subject(text: str, document_type: str) -> str:
    # 🚨 Critical guard
    if document_type == "Resume":
        return "General"

    return classify_by_embedding(text, SUBJECT_VECTORS)
