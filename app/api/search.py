from fastapi import APIRouter, Query, HTTPException

from app.services.semantic_search import semantic_search

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search_documents(
    q: str = Query(..., min_length=2, description="Search query"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Semantic search over documents using embeddings.
    """

    results = semantic_search(query=q, top_k_chunks=top_k)

    if not results:
        return {
            "query": q,
            "results": []
        }

    return {
        "query": q,
        "num_results": len(results),
        "results": results
    }
