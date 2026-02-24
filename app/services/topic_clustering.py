import numpy as np
import hdbscan
import logging
from collections import defaultdict

from app.storage.vector_store import get_all_vectors
from app.storage.metadata import (
    load_chunks,
    load_documents,
    load_clusters,
    save_clusters,
    save_chunks,
    update_document,
)

logger = logging.getLogger(__name__)


def run_topic_clustering(
    user_id: str,
    min_cluster_size: int = 5,
    min_samples: int = 3,
):
    """
    Runs HDBSCAN clustering on chunk embeddings for a specific user.
    Fully user-scoped and safe.
    """

    if not user_id:
        raise ValueError("user_id is required for clustering")

    # ======================================================
    # 1️⃣ Load vectors (user-scoped)
    # ======================================================
    vectors, vector_metadata = get_all_vectors(user_id=user_id)

    if not vectors:
        logger.warning(
            "No vectors found for user %s. Skipping clustering.",
            user_id,
        )
        return []

    if len(vectors) != len(vector_metadata):
        raise RuntimeError(
            "Vector metadata mismatch: vectors and metadata not aligned"
        )

    try:
        X = np.array(vectors, dtype="float32")
    except Exception:
        logger.exception("Failed to convert vectors to numpy array")
        return []

    # ======================================================
    # Load metadata (user filtered)
    # ======================================================
    all_chunks = load_chunks()
    user_chunks = {
        c["chunk_id"]: c
        for c in all_chunks
        if c.get("user_id") == user_id
    }

    all_documents = load_documents()
    user_documents = [
        d for d in all_documents
        if d.get("user_id") == user_id
    ]

    # ======================================================
    # Reset previous cluster assignments
    # ======================================================
    for chunk in user_chunks.values():
        chunk["cluster_id"] = None

    for doc in user_documents:
        update_document(
            doc["doc_id"],
            user_id,
            {"cluster_id": None},
        )

    # ======================================================
    # Small dataset guard
    # ======================================================
    if len(vectors) < max(3, min_samples + 1):
        logger.warning(
            "Not enough data for clustering (user=%s). Assigning default cluster.",
            user_id,
        )

        cluster_id = "cluster_0"

        for chunk in user_chunks.values():
            chunk["cluster_id"] = cluster_id

        save_chunks(all_chunks)

        doc_ids = list({c["doc_id"] for c in user_chunks.values()})

        for doc_id in doc_ids:
            update_document(
                doc_id,
                user_id,
                {"cluster_id": cluster_id},
            )

        # Replace only this user's clusters
        all_clusters = load_clusters()
        all_clusters = [
            c for c in all_clusters
            if c.get("user_id") != user_id
        ]

        all_clusters.append({
            "cluster_id": cluster_id,
            "num_chunks": len(user_chunks),
            "document_ids": doc_ids,
            "user_id": user_id,
        })

        save_clusters(all_clusters)
        return [c for c in all_clusters if c["user_id"] == user_id]

    # ======================================================
    # 2️⃣ Run HDBSCAN
    # ======================================================
    logger.info("Running clustering for user %s", user_id)

    try:
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric="euclidean",
        )
        labels = clusterer.fit_predict(X)
    except Exception:
        logger.exception("HDBSCAN clustering failed")
        return []

    chunk_clusters = defaultdict(list)

    for idx, label in enumerate(labels):

        if label == -1:
            continue

        meta = vector_metadata[idx]

        # Strict user isolation
        if meta.get("user_id") != user_id:
            continue

        chunk_id = meta.get("chunk_id")
        if not chunk_id:
            continue

        chunk = user_chunks.get(chunk_id)
        if not chunk:
            continue

        cluster_id = f"cluster_{label}"
        chunk["cluster_id"] = cluster_id
        chunk_clusters[label].append(chunk)

    # Save updated chunks
    save_chunks(all_chunks)

    # ======================================================
    # Assign cluster to documents
    # ======================================================
    doc_votes = defaultdict(list)

    for label, cluster_chunks in chunk_clusters.items():
        for chunk in cluster_chunks:
            doc_votes[chunk["doc_id"]].append(label)

    for doc_id, votes in doc_votes.items():
        best_cluster = max(set(votes), key=votes.count)
        update_document(
            doc_id,
            user_id,
            {"cluster_id": f"cluster_{best_cluster}"},
        )

    # ======================================================
    # Build cluster metadata (user-scoped)
    # ======================================================
    new_clusters = []

    for label, cluster_chunks in chunk_clusters.items():
        new_clusters.append({
            "cluster_id": f"cluster_{label}",
            "num_chunks": len(cluster_chunks),
            "document_ids": list(
                {c["doc_id"] for c in cluster_chunks}
            ),
            "user_id": user_id,
        })

    all_clusters = load_clusters()
    all_clusters = [
        c for c in all_clusters
        if c.get("user_id") != user_id
    ]
    all_clusters.extend(new_clusters)

    save_clusters(all_clusters)

    logger.info(
        "Clustering complete for user %s. %d clusters created.",
        user_id,
        len(new_clusters),
    )

    return new_clusters