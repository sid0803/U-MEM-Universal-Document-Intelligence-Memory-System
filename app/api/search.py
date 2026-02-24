from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List
import logging

from app.auth.dependencies import get_current_user
from app.services.semantic_search import semantic_search
from app.models.schemas import SearchResult, SearchChunk

router = APIRouter(prefix="/search", tags=["Search"])

logger = logging.getLogger(__name__)


@router.get("/", response_model=List[SearchResult])
def search_documents(
    q: str = Query(..., min_length=2),
    top_k: int = Query(10, ge=1, le=50),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]

    try:
        results = semantic_search(
            query=q,
            top_k=top_k,
            user_id=user_id,
        )

    except ValueError as e:
        logger.warning(
            "Search validation error | user=%s | query=%s | error=%s",
            user_id, q, str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception("Search failed | user=%s | query=%s", user_id, q)
        raise HTTPException(status_code=500, detail="Search failed")

    formatted_results: List[SearchResult] = []

    for r in results:
        # Ensure matched_chunks always valid list
        chunks = r.get("matched_chunks") or []

        formatted_results.append(
            SearchResult(
                doc_id=r.get("doc_id"),
                score=float(r.get("score", 0.0)),
                confidence=r.get("confidence", "low"),
                document_type=r.get("document_type"),
                subject=r.get("subject"),
                original_name=r.get("original_name"),
                matched_chunks=[
                    SearchChunk(**chunk) for chunk in chunks
                ],
            )
        )

    return formatted_results
