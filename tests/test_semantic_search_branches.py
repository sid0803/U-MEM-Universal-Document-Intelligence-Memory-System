import pytest
from app.services.semantic_search import semantic_search, rag_ask


def test_semantic_search_empty_query():
    result = semantic_search("", user_id="u1")
    assert result == []


def test_semantic_search_requires_user():
    with pytest.raises(ValueError):
        semantic_search("hello", user_id=None)


def test_rag_ask_no_results():
    result = rag_ask("some random question", user_id="nonexistent_user")
    assert result["answer"] == "Not found in documents"
    assert result["citations"] == []