# app/core/job_types.py

from enum import Enum


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class JobType(str, Enum):
    UPLOAD = "UPLOAD"
    CLUSTERING = "CLUSTERING"
