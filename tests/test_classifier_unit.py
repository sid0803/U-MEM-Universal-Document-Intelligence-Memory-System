import pytest
from unittest.mock import patch

from app.services.classifier import (
    classify_by_embedding,
    classify_document_type,
    classify_subject,
)


# -----------------------------------------
# Test classify_by_embedding
# -----------------------------------------

def test_classify_by_embedding_empty_text():
    result = classify_by_embedding("", {"AI": [1, 0]})
    assert result == "General"


def test_classify_by_embedding_best_match():
    with patch("app.services.classifier.embed_text") as mock_embed, \
         patch("app.services.classifier.cosine_similarity") as mock_cosine:

        mock_embed.return_value = [1, 0]

        # Simulate similarity scores
        def fake_similarity(v1, v2):
            if v2 == [1, 0]:
                return 0.9
            return 0.2

        mock_cosine.side_effect = fake_similarity

        reference_vectors = {
            "AI": [1, 0],
            "Finance": [0, 1]
        }

        result = classify_by_embedding("some text", reference_vectors)
        assert result == "AI"


# -----------------------------------------
# Test classify_document_type
# -----------------------------------------

def test_classify_document_type():
    with patch("app.services.classifier.embed_text") as mock_embed, \
         patch("app.services.classifier.cosine_similarity") as mock_cosine:

        mock_embed.return_value = [1, 0]
        mock_cosine.return_value = 0.8

        result = classify_document_type("This is a resume document")
        assert result in ["Resume", "Research_Paper", "Invoice", "Notes"]


# -----------------------------------------
# Test classify_subject
# -----------------------------------------

def test_classify_subject_resume_guard():
    result = classify_subject("some text", document_type="Resume")
    assert result == "General"


def test_classify_subject_normal_flow():
    with patch("app.services.classifier.embed_text") as mock_embed, \
         patch("app.services.classifier.cosine_similarity") as mock_cosine:

        mock_embed.return_value = [1, 0]
        mock_cosine.return_value = 0.9

        result = classify_subject("AI content", document_type="Notes")
        assert result in ["AI", "Database", "Finance", "General"]