# app/api/clusters.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from typing import List
from pydantic import BaseModel, Field
import logging
import traceback

from app.auth.dependencies import get_current_user
from app.storage.metadata import load_clusters, load_documents
from app.core.jobs import create_job
from app.core.job_store import update_job, get_all_jobs
from app.core.job_types import JobType, JobStatus
from app.services.topic_clustering import run_topic_clustering
from app.core.security_utils import validate_ownership

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clusters", tags=["Clusters"])


# =========================================================
# Response Schemas
# =========================================================

class ClusterSummary(BaseModel):
    cluster_id: str
    num_documents: int
    label: str | None = None
    keywords: List[str] = Field(default_factory=list)


class ClusterDocumentsResponse(BaseModel):
    cluster_id: str
    num_documents: int
    documents: List[dict]


class JobTriggerResponse(BaseModel):
    job_id: str
    status: str


# =========================================================
# Utility
# =========================================================

def clustering_running(user_id: str) -> bool:
    """
    Prevent duplicate clustering jobs per user.
    """
    try:
        jobs = get_all_jobs(user_id=user_id)
    except Exception:
        logger.exception("Failed to fetch jobs")
        return False

    return any(
        job["status"] in [
            JobStatus.PENDING.value,
            JobStatus.RUNNING.value,
        ]
        for job in jobs
    )


def safe_load_clusters():
    try:
        return load_clusters()
    except Exception:
        logger.exception("Failed to load clusters")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cluster storage unavailable",
        )


def safe_load_documents():
    try:
        return load_documents()
    except Exception:
        logger.exception("Failed to load documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document storage unavailable",
        )


# =========================================================
# API Endpoints
# =========================================================

@router.get("/", response_model=List[ClusterSummary])
def list_clusters(current_user=Depends(get_current_user)):
    user_id = current_user["user_id"]
    clusters = safe_load_clusters()

    user_clusters = [
        c for c in clusters if c.get("user_id") == user_id
    ]

    return [
        ClusterSummary(
            cluster_id=c["cluster_id"],
            num_documents=len(c.get("document_ids", [])),
            label=c.get("label"),
            keywords=c.get("keywords", []),
        )
        for c in user_clusters
    ]


@router.get("/{cluster_id}/documents", response_model=ClusterDocumentsResponse)
def get_cluster_documents(cluster_id: str, current_user=Depends(get_current_user)):
    user_id = current_user["user_id"]

    clusters = safe_load_clusters()
    documents = safe_load_documents()

    cluster = next(
        (c for c in clusters if c.get("cluster_id") == cluster_id),
        None,
    )

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    validate_ownership(cluster, user_id)

    cluster_docs = [
        d for d in documents
        if d.get("cluster_id") == cluster_id
        and d.get("user_id") == user_id
    ]

    return ClusterDocumentsResponse(
        cluster_id=cluster_id,
        num_documents=len(cluster_docs),
        documents=cluster_docs,
    )


# =========================================================
# Background Job Logic
# =========================================================

def clustering_background_job(job_id: str, user_id: str):
    """
    Background clustering execution.
    Always updates job lifecycle.
    """
    logger.info("Background task started | job=%s user=%s", job_id, user_id)

    try:
        # Mark RUNNING
        update_job(
            job_id=job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Clustering started",
            progress=10,
        )

        clusters = run_topic_clustering(user_id=user_id)

        if clusters is None:
            raise RuntimeError("Clustering returned None")

        # Mark SUCCESS
        update_job(
            job_id=job_id,
            user_id=user_id,
            status=JobStatus.SUCCESS,
            message="Clustering completed",
            progress=100,
        )

        logger.info("Clustering completed | job=%s", job_id)

    except Exception as e:
        logger.error("Clustering failed | job=%s", job_id)
        logger.error(traceback.format_exc())

        try:
            update_job(
                job_id=job_id,
                user_id=user_id,
                status=JobStatus.FAILED,
                error=str(e),
                progress=100,
            )
        except Exception:
            logger.error("CRITICAL: Failed to update job after crash")


# =========================================================
# Trigger Clustering
# =========================================================

@router.post("/run", response_model=JobTriggerResponse)
async def run_clustering(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]

    if clustering_running(user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Clustering already running",
        )

    documents = safe_load_documents()
    user_docs = [d for d in documents if d.get("user_id") == user_id]

    if not user_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents available for clustering",
        )

    job_id = create_job(JobType.CLUSTERING, user_id)

    background_tasks.add_task(
        clustering_background_job,
        job_id,
        user_id,
    )

    return JobTriggerResponse(
        job_id=job_id,
        status=JobStatus.PENDING.value,
    )
