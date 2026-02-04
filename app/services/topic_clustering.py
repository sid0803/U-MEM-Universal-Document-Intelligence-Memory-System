import numpy as np
import hdbscan
from collections import defaultdict

from app.storage.vector_store import get_all_vectors
from app.storage.metadata import (
    load_chunks,
    load_documents,
    save_clusters,
    save_chunks,
    update_document
)


def run_topic_clustering(
    min_cluster_size: int = 5,
    min_samples: int = 3
):
    """
    Runs HDBSCAN clustering on chunk embeddings.
    """

    # 1️⃣ Load all vectors (chunk embeddings)
    vectors, vector_metadata = get_all_vectors()

    if len(vectors) == 0:
        print("⚠️ No vectors found. Skipping clustering.")
        return []

    X = np.array(vectors, dtype="float32")
    num_points = X.shape[0]

    # ======================================================
    # 🔐 OPTION B: SAFETY GUARD FOR SMALL DATASETS
    # ======================================================
    if num_points < max(3, min_samples + 1):
        print(f"⚠️ Not enough data points for clustering ({num_points}).")

        chunks = load_chunks()
        documents = load_documents()

        doc_ids = list({c["doc_id"] for c in chunks})
        cluster_id = "cluster_0"

        # Assign default cluster to chunks
        for c in chunks:
            c["cluster_id"] = cluster_id

        save_chunks(chunks)

        # Assign default cluster to documents
        for doc_id in doc_ids:
            update_document(doc_id, {"cluster_id": cluster_id})

        clusters = [{
            "cluster_id": cluster_id,
            "num_chunks": len(chunks),
            "document_ids": doc_ids
        }]

        save_clusters(clusters)
        print("✅ Assigned default cluster (single-cluster case).")
        return clusters

    # ======================================================
    # 2️⃣ Run HDBSCAN (normal case)
    # ======================================================
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="cosine"  # better for normalized embeddings
    )

    labels = clusterer.fit_predict(X)

    # 3️⃣ Load metadata
    chunks = load_chunks()

    chunk_by_vector = {
        c["vector_id"]: c for c in chunks
    }

    # 4️⃣ Assign cluster_id to chunks
    chunk_clusters = defaultdict(list)

    for vector_id, label in enumerate(labels):
        if label == -1:
            continue  # noise

        chunk = chunk_by_vector.get(vector_id)
        if not chunk:
            continue

        chunk["cluster_id"] = f"cluster_{label}"
        chunk_clusters[label].append(chunk)

    save_chunks(chunks)

    # 5️⃣ Assign cluster to documents (majority vote)
    doc_cluster_votes = defaultdict(list)

    for cluster_label, cluster_chunks in chunk_clusters.items():
        for chunk in cluster_chunks:
            doc_cluster_votes[chunk["doc_id"]].append(cluster_label)

    document_clusters = {}
    for doc_id, votes in doc_cluster_votes.items():
        best_cluster = max(set(votes), key=votes.count)
        document_clusters[doc_id] = f"cluster_{best_cluster}"

    for doc_id, cluster_id in document_clusters.items():
        update_document(doc_id, {"cluster_id": cluster_id})

    # 6️⃣ Build cluster metadata
    clusters = []

    for cluster_label, cluster_chunks in chunk_clusters.items():
        clusters.append({
            "cluster_id": f"cluster_{cluster_label}",
            "num_chunks": len(cluster_chunks),
            "document_ids": list(
                {c["doc_id"] for c in cluster_chunks}
            )
        })

    # 7️⃣ Persist clusters
    save_clusters(clusters)

    print("✅ Clustering completed successfully.")
    return clusters


print("Loaded topic_clustering.py")
print("Functions:", dir())
