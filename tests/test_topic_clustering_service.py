import uuid
from app.services.topic_clustering import run_topic_clustering
from app.storage.metadata import create_document, add_chunks


def test_topic_clustering_with_minimal_data():
    user_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())

    # Create fake document
    create_document(
        doc_id=doc_id,
        original_name="test.txt",
        file_type="txt",
        num_chunks=1,
        user_id=user_id,
    )

    add_chunks([
        {
            "chunk_id": str(uuid.uuid4()),
            "doc_id": doc_id,
            "text": "Artificial intelligence clustering test",
            "user_id": user_id,
        }
    ])

    clusters = run_topic_clustering(user_id=user_id)

    assert clusters is not None