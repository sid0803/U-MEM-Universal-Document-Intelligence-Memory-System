from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

from app.storage.metadata import load_clusters, load_chunks, save_clusters


def label_clusters(
    top_k_keywords: int = 5
):
    """
    Auto-label clusters using TF-IDF keywords.
    """

    clusters = load_clusters()
    if not clusters:
        return []

    chunks = load_chunks()

    # Build cluster_id -> texts
    cluster_texts = defaultdict(list)

    for c in chunks:
        cluster_id = c.get("cluster_id")
        if cluster_id:
            cluster_texts[cluster_id].append(c["text"])

    updated_clusters = []

    for cluster in clusters:
        cid = cluster["cluster_id"]
        texts = cluster_texts.get(cid, [])

        if not texts:
            cluster["label"] = "Miscellaneous"
            cluster["keywords"] = []
            updated_clusters.append(cluster)
            continue

        # TF-IDF
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=1000
        )
        tfidf = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()

        scores = tfidf.mean(axis=0).A1
        top_indices = scores.argsort()[-top_k_keywords:][::-1]

        keywords = [feature_names[i] for i in top_indices]

        # Simple human-readable label
        label = " / ".join(keywords[:2]).title()

        cluster["keywords"] = keywords
        cluster["label"] = label

        updated_clusters.append(cluster)

    save_clusters(updated_clusters)
    return updated_clusters
