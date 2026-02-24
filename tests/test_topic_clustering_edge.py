import pytest
from app.services.topic_clustering import run_topic_clustering


def test_clustering_requires_user():
    with pytest.raises(ValueError):
        run_topic_clustering(user_id=None)


def test_clustering_no_vectors(monkeypatch):
    # Mock get_all_vectors to return empty
    monkeypatch.setattr(
        "app.services.topic_clustering.get_all_vectors",
        lambda user_id: ([], []),
    )

    result = run_topic_clustering(user_id="u1")
    assert result == []


def test_clustering_metadata_mismatch(monkeypatch):
    # Force mismatch: 2 vectors but 1 metadata
    monkeypatch.setattr(
        "app.services.topic_clustering.get_all_vectors",
        lambda user_id: (
            [[0.1, 0.2], [0.3, 0.4]],   # 2 vectors
            [{"chunk_id": "c1", "user_id": user_id}],  # 1 metadata only
        ),
    )

    with pytest.raises(RuntimeError):
        run_topic_clustering(user_id="u1")