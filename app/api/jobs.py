# app/api/jobs.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from pydantic import BaseModel
import logging

from app.auth.dependencies import get_current_user
from app.core.job_store import get_job, get_all_jobs
from app.models.job import JobResponse
from app.core.security_utils import validate_ownership
from app.core.job_types import JobStatus, JobType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# =========================================================
# Response Schemas
# =========================================================

class JobListResponse(BaseModel):
    count: int
    jobs: List[JobResponse]


# =========================================================
# Helpers
# =========================================================

def map_job_row(row: dict) -> JobResponse:
    """
    Convert raw DB row into validated JobResponse model.
    """
    try:
        return JobResponse(
            job_id=row["job_id"],
            user_id=row["user_id"],
            type=row["job_type"],
            status=row["status"],
            message=row.get("message", ""),
            progress=row.get("progress", 0),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    except Exception:
        logger.exception("Failed to map job row: %s", row)
        raise


# =========================================================
# API Endpoints
# =========================================================

@router.get("/", response_model=JobListResponse)
def list_jobs(current_user: Dict[str, str] = Depends(get_current_user)):
    user_id = current_user["user_id"]

    try:
        rows = get_all_jobs(user_id)
        jobs = [map_job_row(r) for r in rows]

    except Exception:
        logger.exception("Failed to fetch jobs for user=%s", user_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to load jobs",
        )

    return JobListResponse(
        count=len(jobs),
        jobs=jobs,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: str,
    current_user: Dict[str, str] = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    try:
        row = get_job(job_id, user_id)

    except Exception:
        logger.exception("Failed to fetch job %s", job_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to load job",
        )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    validate_ownership(row, user_id)

    return map_job_row(row)
