from collections import defaultdict
from app.storage.metadata import load_clusters, load_chunks, save_clusters


def summarize_clusters():
    """
    Generate short summaries for each cluster using chunk text.
    """

    clusters = load_clusters()
    if not clusters:
        return []

    chunks = load_chunks()

    cluster_texts = defaultdict(list)
    for c in chunks:
        if c.get("cluster_id"):
            cluster_texts[c["cluster_id"]].append(c["text"])

    for cluster in clusters:
        cid = cluster["cluster_id"]
        texts = cluster_texts.get(cid, [])

        if not texts:
            cluster["summary"] = "No sufficient content to summarize."
            continue

        # Simple heuristic summary (LLM-ready later)
        preview = " ".join(texts[:3])[:400]
        cluster["summary"] = (
            f"This cluster contains documents related to: {cluster.get('label', 'general topics')}. "
            f"Sample content: {preview}..."
        )

    save_clusters(clusters)
    return clusters
