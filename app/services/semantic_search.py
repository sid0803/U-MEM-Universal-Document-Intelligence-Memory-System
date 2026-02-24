import math
import logging
from collections import defaultdict
from typing import List, Dict

from app.services.embeddings import embed_text
from app.storage.vector_store import search_similar
from app.storage.metadata import load_documents, load_chunks
from app.services.llm import ask_llm

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.25
MAX_QUERY_LENGTH = 512
MAX_CHUNK_PREVIEW = 300


# ==========================================================
# USER-SCOPED SEMANTIC SEARCH
# ==========================================================

def semantic_search(
    query: str,
    user_id: str,
    top_k: int = 5,
) -> List[Dict]:

    if not user_id:
        raise ValueError("user_id is required for semantic search")

    if not query or not query.strip():
        return []

    if top_k <= 0:
        top_k = 5

    query = query.strip()[:MAX_QUERY_LENGTH]

    logger.info(
        "Semantic search started | user=%s | query=%s",
        user_id,
        query,
    )

    # 1️⃣ Embed query
    try:
        query_embedding = embed_text(query)
        if not query_embedding:
            return []
    except Exception:
        logger.exception("Embedding failed | user=%s", user_id)
        return []

    # 2️⃣ Vector search
    try:
        hits = search_similar(
            query_embedding,
            k=top_k,
            user_id=user_id,
        )
    except Exception:
        logger.exception("Vector search failed | user=%s", user_id)
        return []

    if not hits:
        return []

    # 3️⃣ Load metadata safely
    documents = {}
    for d in load_documents():
        if d.get("user_id") != user_id:
            continue
        if not d.get("doc_id"):
            continue
        documents[d["doc_id"]] = d

    chunks = {}
    for c in load_chunks():
        if c.get("user_id") != user_id:
            continue
        if not c.get("chunk_id"):
            continue
        chunks[c["chunk_id"]] = c

    doc_scores = defaultdict(list)
    doc_chunks = defaultdict(list)

    # 4️⃣ Aggregate chunk scores
    for hit in hits:

        score = float(hit.get("score", 0))
        if score < SIMILARITY_THRESHOLD:
            continue

        chunk_id = hit.get("chunk_id")
        doc_id = hit.get("doc_id")

        if not chunk_id or not doc_id:
            continue

        if doc_id not in documents:
            continue

        chunk = chunks.get(chunk_id)
        if not chunk:
            continue

        doc_scores[doc_id].append(score)

        doc_chunks[doc_id].append({
            "chunk_id": chunk_id,
            "score": round(score, 4),
            "text": chunk.get("text", "")[:MAX_CHUNK_PREVIEW],
        })

    # 5️⃣ Rank documents
    ranked = []

    for doc_id, scores in doc_scores.items():
        if not scores:
            continue

        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        freq_bonus = math.log(1 + len(scores))

        final_score = (
            0.6 * max_score +
            0.3 * avg_score +
            0.1 * freq_bonus
        )

        ranked.append((doc_id, round(final_score, 4)))

    ranked.sort(key=lambda x: x[1], reverse=True)

    # 6️⃣ Build response
    results = []

    for doc_id, score in ranked[:top_k]:

        doc = documents.get(doc_id)
        if not doc:
            continue

        confidence = (
            "high" if score >= 0.6 else
            "medium" if score >= 0.4 else
            "low"
        )

        results.append({
            "doc_id": doc_id,
            "score": score,
            "confidence": confidence,
            "original_name": doc.get("original_name"),
            "file_type": doc.get("file_type"),
            "cluster_id": doc.get("cluster_id"),
            "matched_chunks": sorted(
                doc_chunks[doc_id],
                key=lambda x: x["score"],
                reverse=True,
            )[:3],
        })

    logger.info(
        "Semantic search complete | user=%s | results=%d",
        user_id,
        len(results),
    )

    return results

def rag_ask(
    query: str,
    user_id: str,
    top_k: int = 5,
) -> Dict:

    search_results = semantic_search(
        query=query,
        user_id=user_id,
        top_k=top_k,
    )

    if not search_results:
        return {
            "question": query,
            "answer": "Not found in documents",
            "citations": [],
        }

    context_parts = []
    citations = []
    seen_chunks = set()

    for doc in search_results:
        for chunk in doc["matched_chunks"]:

            cid = chunk["chunk_id"]
            if cid in seen_chunks:
                continue

            seen_chunks.add(cid)

            context_parts.append(chunk["text"])
            citations.append({
                "doc_id": doc["doc_id"],
                "chunk_id": cid,
                "score": chunk["score"],
                "source": doc.get("original_name"),
            })

            if len(context_parts) >= top_k:
                break

        if len(context_parts) >= top_k:
            break

    if not context_parts:
        return {
            "question": query,
            "answer": "Not found in documents",
            "citations": [],
        }

    context = "\n\n".join(context_parts)

    try:
        answer = ask_llm(context, query)
    except Exception:
        logger.exception("LLM generation failed | user=%s", user_id)
        answer = "Error generating answer."

    return {
        "question": query,
        "answer": answer,
        "citations": citations[:top_k],
    }
