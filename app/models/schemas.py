# app/models/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import List
from app.core.job_types import JobStatus
from typing import List, Optional


# --------------------------------------------------
# Upload (Async Job Start Response)
# --------------------------------------------------
class UploadJobResponse(BaseModel):
    job_id: str
    status: JobStatus
    filename: str

    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------
# Upload (After Processing Completed - Optional Future)
# --------------------------------------------------
class UploadResultResponse(BaseModel):
    doc_id: str
    filename: str
    document_type: str
    subject: str
    chunks_created: int

    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------
# Search Models
# --------------------------------------------------
class SearchChunk(BaseModel):
    chunk_id: str
    score: float
    text: str

    model_config = ConfigDict(extra="forbid")

class SearchResult(BaseModel):
    doc_id: str
    score: float
    confidence: str
    document_type: Optional[str] = None
    subject: Optional[str] = None
    original_name: str
    matched_chunks: List[SearchChunk]


