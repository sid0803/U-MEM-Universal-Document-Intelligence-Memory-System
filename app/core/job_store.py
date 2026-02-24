# app/core/job_store.py

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, UTC
from typing import List, Optional
from contextlib import contextmanager
import os

from app.core.job_types import JobStatus, JobType

logger = logging.getLogger(__name__)

# Allow override in tests via environment variable
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "jobs.db"


# =========================================================
# Connection Manager
# =========================================================

@contextmanager
def get_connection():
    """
    Production-safe SQLite connection manager.
    Always closes connection.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        isolation_level=None 
    )
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


# =========================================================
# DB Initialization
# =========================================================

def init_db():
    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL,
                message TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                user_id TEXT NOT NULL
            )
        """)

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)"
        )


init_db()


# =========================================================
# Write Operations
# =========================================================

def insert_job(job_id: str, job_type: JobType | str, user_id: str):
    if isinstance(job_type, JobType):
        job_type_value = job_type.value
    elif isinstance(job_type, str):
        job_type_value = job_type
    else:
        raise ValueError("Invalid job_type")

    now = datetime.now(UTC).isoformat()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO jobs (
                job_id, job_type, status, progress,
                message, error, created_at, updated_at, user_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            job_type_value,
            JobStatus.PENDING.value,
            0,
            "",
            None,
            now,
            now,
            user_id,
        ))


def update_job(
    job_id: str,
    user_id: str,
    status: Optional[JobStatus | str] = None,
    progress: Optional[int] = None,
    message: Optional[str] = None,
    error: Optional[str] = None
):
    now = datetime.now(UTC).isoformat()

    fields = []
    values = []

    # -------- Status --------
    if status is not None:
        if isinstance(status, JobStatus):
            values.append(status.value)
        elif isinstance(status, str):
            values.append(status)
        else:
            raise ValueError("Invalid status")

        fields.append("status = ?")

    # -------- Progress --------
    if progress is not None:
        if not (0 <= progress <= 100):
            raise ValueError("Progress must be between 0 and 100")
        fields.append("progress = ?")
        values.append(progress)

    # -------- Message --------
    if message is not None:
        fields.append("message = ?")
        values.append(message)

    # -------- Error --------
    if error is not None:
        fields.append("error = ?")
        values.append(error)

    if not fields:
        return

    fields.append("updated_at = ?")
    values.append(now)

    values.extend([job_id, user_id])

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE jobs SET {', '.join(fields)} "
            "WHERE job_id = ? AND user_id = ?",
            values
        )

        
        if cursor.rowcount == 0:
            logger.error(
            "Job update failed | job_id=%s | user_id=%s",
            job_id,
            user_id,
        )
            raise ValueError("Job not found or access denied")
            

# =========================================================
# Read Operations
# =========================================================

def get_job(job_id: str, user_id: str) -> Optional[dict]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM jobs WHERE job_id = ? AND user_id = ?",
            (job_id, user_id)
        )
        row = cursor.fetchone()

    return dict(row) if row else None


def get_all_jobs(user_id: Optional[str] = None) -> List[dict]:
    with get_connection() as conn:
        if user_id:
            cursor = conn.execute(
                "SELECT * FROM jobs WHERE user_id = ? "
                "ORDER BY created_at DESC",
                (user_id,)
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC"
            )

        rows = cursor.fetchall()

    return [dict(r) for r in rows]