# app/models/job.py

from pydantic import BaseModel
from typing import Optional
from app.core.job_types import JobStatus


class JobResponse(BaseModel):
    job_id: str
    user_id: str
    type: str
    status: JobStatus
    message: Optional[str] = None
    progress: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
