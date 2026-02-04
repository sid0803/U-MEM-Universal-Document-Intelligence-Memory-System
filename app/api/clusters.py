from fastapi import APIRouter, HTTPException

from app.storage.metadata import (
    load_clusters,
    load_documents
)

router = APIRouter(prefix="/clusters", tags=["Clusters"])


@router.get("/")
def list_clusters():
    """
    List all clusters with basic info.
    """
    clusters = load_clusters()

    if not clusters:
        return []

    response = []
    for c in clusters:
        response.append({
            "cluster_id": c["cluster_id"],
            "num_documents": len(c.get("document_ids", [])),
            "label": c.get("label"),
            "keywords": c.get("keywords", [])
        })

    return response


@router.get("/{cluster_id}/documents")
def get_cluster_documents(cluster_id: str):
    """
    Get all documents belonging to a cluster.
    """
    documents = load_documents()

    cluster_docs = [
        d for d in documents
        if d.get("cluster_id") == cluster_id
    ]

    if not cluster_docs:
        raise HTTPException(
            status_code=404,
            detail=f"No documents found for cluster {cluster_id}"
        )

    return {
        "cluster_id": cluster_id,
        "num_documents": len(cluster_docs),
        "documents": cluster_docs
    }
