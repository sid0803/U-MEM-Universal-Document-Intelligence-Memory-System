from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

from app.storage.metadata import (
    load_clusters,
    load_chunks,
    save_clusters,
)


def label_clusters(
    user_id: str,
    top_k_keywords: int = 5,
):
    """
    Auto-label clusters using TF-IDF keywords for a specific user.
    """

    if not user_id:
        raise ValueError("user_id is required for labeling clusters")

    all_clusters = load_clusters()
    all_chunks = load_chunks()

    # Filter per user
    clusters = [c for c in all_clusters if c.get("user_id") == user_id]
    chunks = [c for c in all_chunks if c.get("user_id") == user_id]

    if not clusters:
        return []

    # Build cluster_id -> texts
    cluster_texts = defaultdict(list)

    for c in chunks:
        cluster_id = c.get("cluster_id")
        text = c.get("text")

        if cluster_id and text:
            cluster_texts[cluster_id].append(text)

    updated_clusters = []

    for cluster in clusters:
        cid = cluster["cluster_id"]
        texts = cluster_texts.get(cid, [])

        if not texts:
            cluster["label"] = "Miscellaneous"
            cluster["keywords"] = []
            updated_clusters.append(cluster)
            continue

        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=1000,
        )

        tfidf = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()

        scores = tfidf.mean(axis=0).A1
        top_indices = scores.argsort()[-top_k_keywords:][::-1]

        keywords = [feature_names[i] for i in top_indices]

        label = " / ".join(keywords[:2]).title()

        cluster["keywords"] = keywords
        cluster["label"] = label

        updated_clusters.append(cluster)

    # 🔐 Merge safely with other users
    remaining_clusters = [
        c for c in all_clusters if c.get("user_id") != user_id
    ]

    remaining_clusters.extend(updated_clusters)

    save_clusters(remaining_clusters)

    return updated_clusters
