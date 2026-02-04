import math
from collections import defaultdict

from app.services.embeddings import embed_text
from app.storage.vector_store import search_similar
from app.storage.metadata import load_documents, load_chunks
from app.storage.vector_store import load_vector_metadata


def semantic_search(query: str, top_k_chunks: int = 10):
    # 1️⃣ Embed query
    query_embedding = embed_text(query)

    # 2️⃣ Search FAISS (returns vector_id + score)
    chunk_hits = search_similar(query_embedding, k=top_k_chunks)
    if not chunk_hits:
        return []

    # 3️⃣ Load metadata
    documents = {d["doc_id"]: d for d in load_documents()}
    chunks = {c["chunk_id"]: c for c in load_chunks()}
    vector_meta = load_vector_metadata()

    vector_to_chunk = {
        v["vector_id"]: v for v in vector_meta
    }

    # 4️⃣ Collect chunk scores per document
    doc_chunk_scores = defaultdict(list)
    doc_chunks = defaultdict(list)

    for hit in chunk_hits:
        vector_id = hit["vector_id"]
        score = hit["score"]

        meta = vector_to_chunk.get(vector_id)
        if not meta:
            continue

        chunk_id = meta["chunk_id"]
        doc_id = meta["doc_id"]

        chunk = chunks.get(chunk_id)
        if not chunk:
            continue

        doc_chunk_scores[doc_id].append(score)

        doc_chunks[doc_id].append({
            "chunk_id": chunk["chunk_id"],
            "score": score,
            "text": chunk["text"][:300]
        })

    # 5️⃣ Compute final document scores
    doc_final_scores = {}

    for doc_id, scores in doc_chunk_scores.items():
        best = max(scores)
        avg = sum(scores) / len(scores)
        count = len(scores)

        final_score = (
            0.6 * best +
            0.3 * avg +
            0.1 * math.log(1 + count)
        )

        doc_final_scores[doc_id] = final_score

    # 6️⃣ Rank documents
    ranked_docs = sorted(
        doc_final_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # 7️⃣ Build response
    results = []
    for doc_id, score in ranked_docs:
        doc = documents.get(doc_id)
        if not doc:
            continue

        results.append({
            "doc_id": doc_id,
            "score": score,
            "document_type": doc["document_type"],
            "subject": doc["subject"],
            "original_name": doc["original_name"],
            "path": doc["path"],
            "cluster_id": doc.get("cluster_id"),
            "matched_chunks": sorted(
                doc_chunks[doc_id],
                key=lambda x: x["score"],
                reverse=True
            )[:3]  # top chunks only
        })

    return results
