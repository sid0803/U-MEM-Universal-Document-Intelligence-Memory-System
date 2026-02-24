from app.services.topic_clustering import run_topic_clustering


def test_clustering_small_dataset(monkeypatch):

    # 1️⃣ Mock vectors smaller than threshold
    monkeypatch.setattr(
        "app.services.topic_clustering.get_all_vectors",
        lambda user_id: (
            [[0.1, 0.2]],  # one vector only
            [{"chunk_id": "c1", "doc_id": "d1", "user_id": user_id}],
        ),
    )

    monkeypatch.setattr(
        "app.services.topic_clustering.load_chunks",
        lambda: [
            {"chunk_id": "c1", "doc_id": "d1", "user_id": "u1"}
        ],
    )

    monkeypatch.setattr(
        "app.services.topic_clustering.load_documents",
        lambda: [
            {"doc_id": "d1", "user_id": "u1"}
        ],
    )

    monkeypatch.setattr(
        "app.services.topic_clustering.load_clusters",
        lambda: [],
    )

    monkeypatch.setattr(
        "app.services.topic_clustering.save_clusters",
        lambda clusters: None,
    )

    monkeypatch.setattr(
        "app.services.topic_clustering.save_chunks",
        lambda chunks: None,
    )

    monkeypatch.setattr(
        "app.services.topic_clustering.update_document",
        lambda doc_id, user_id, data: None,
    )

    result = run_topic_clustering(user_id="u1")

    assert isinstance(result, list)