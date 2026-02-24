from collections import Counter
from app.storage.metadata import load_clusters, load_chunks, save_clusters


def assign_cluster_confidence(user_id: str):
    clusters = load_clusters()
    chunks = load_chunks()

    # Filter by user
    user_clusters = [c for c in clusters if c.get("user_id") == user_id]
    user_chunks = [c for c in chunks if c.get("user_id") == user_id]

    if not user_chunks:
        return []

    # Count chunks per cluster
    cluster_counts = Counter(
        c.get("cluster_id")
        for c in user_chunks
        if c.get("cluster_id") is not None
    )

    total_user_chunks = len(user_chunks)

    for cluster in user_clusters:
        cid = cluster.get("cluster_id")
        if cid is None:
            cluster["confidence"] = 0.0
            continue

        count = cluster_counts.get(cid, 0)

        # Confidence = % of user's chunks belonging to this cluster
        cluster["confidence"] = round(count / total_user_chunks, 3)

    # Update only user clusters
    updated_clusters = []
    for cluster in clusters:
        if cluster.get("user_id") == user_id:
            updated_clusters.append(
                next(c for c in user_clusters if c["cluster_id"] == cluster["cluster_id"])
            )
        else:
            updated_clusters.append(cluster)

    save_clusters(updated_clusters)
    return user_clusters
