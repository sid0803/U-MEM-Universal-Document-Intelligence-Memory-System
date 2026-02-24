from app.services.semantic_search import semantic_search


def test_semantic_search_confidence_levels(monkeypatch):

    monkeypatch.setattr(
        "app.services.semantic_search.embed_text",
        lambda q: [0.1, 0.2],
    )

    monkeypatch.setattr(
        "app.services.semantic_search.search_similar",
        lambda emb, k, user_id: [
            {"score": 0.8, "chunk_id": "c1", "doc_id": "d1"},
        ],
    )

    monkeypatch.setattr(
        "app.services.semantic_search.load_documents",
        lambda: [
            {"doc_id": "d1", "user_id": "u1", "original_name": "file.txt"}
        ],
    )

    monkeypatch.setattr(
        "app.services.semantic_search.load_chunks",
        lambda: [
            {"chunk_id": "c1", "doc_id": "d1", "user_id": "u1", "text": "hello world"}
        ],
    )

    result = semantic_search("test", user_id="u1")

    assert result[0]["confidence"] in ["high", "medium", "low"]