from app.storage.metadata import load_documents, load_clusters


def test_metadata_load_functions():
    docs = load_documents()
    clusters = load_clusters()

    assert isinstance(docs, list)
    assert isinstance(clusters, list)