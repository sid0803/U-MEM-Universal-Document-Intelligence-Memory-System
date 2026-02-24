from pathlib import Path
import uuid
import logging

from app.core.job_store import insert_job, update_job
from app.core.job_types import JobType, JobStatus

from app.services.file_detector import detect_file_type
from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts

from app.storage.metadata import create_document, add_chunks
from app.storage.vector_store import add_vectors


logger = logging.getLogger(__name__)


# ==========================================================
# Job Creation
# ==========================================================
def create_job(job_type: JobType | str, user_id: str) -> str:
    job_id = str(uuid.uuid4())

    if isinstance(job_type, JobType):
        job_type = job_type.value

    insert_job(job_id, job_type, user_id)

    logger.info("Job created | job_id=%s | user_id=%s", job_id, user_id)

    return job_id


# ==========================================================
# Upload Processing Worker
# ==========================================================
def process_upload(
    job_id: str,
    file_path: Path,
    original_filename: str,
    user_id: str,
):
    """
    Background upload processing pipeline.
    """

    try:
        # --------------------------------------------------
        # 1️⃣ Detect file type
        # --------------------------------------------------
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Detecting file type",
            progress=10,
        )

        file_type = detect_file_type(file_path)

        # --------------------------------------------------
        # 2️⃣ Extract text
        # --------------------------------------------------
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Extracting text",
            progress=30,
        )

        text = extract_text(str(file_path), file_type)

        if not text or not text.strip():
            raise ValueError("Empty document content")

        # --------------------------------------------------
        # 3️⃣ Chunk text
        # --------------------------------------------------
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Chunking text",
            progress=50,
        )

        raw_chunks = chunk_text(text)

        if not raw_chunks:
            raise ValueError("Chunking produced no content")

        if isinstance(raw_chunks[0], dict):
            raw_chunks = [c["text"] for c in raw_chunks]

        # --------------------------------------------------
        # 4️⃣ Embed chunks
        # --------------------------------------------------
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Embedding chunks",
            progress=70,
        )

        embeddings = embed_texts(raw_chunks)

        if not embeddings or len(raw_chunks) != len(embeddings):
            raise ValueError("Embedding generation failed")

        # --------------------------------------------------
        # 5️⃣ Generate Document ID
        # --------------------------------------------------
        doc_id = str(uuid.uuid4())

        structured_chunks = []

        for chunk_text_value in raw_chunks:
            structured_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "doc_id": doc_id,
                "text": chunk_text_value,
                "user_id": user_id,
            })

        # --------------------------------------------------
        # 6️⃣ Save Document Metadata
        # --------------------------------------------------
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Saving metadata",
            progress=80,
        )

        create_document(
            doc_id=doc_id,
            original_name=original_filename,
            file_type=file_type,
            num_chunks=len(structured_chunks),
            user_id=user_id,
        )

        add_chunks(structured_chunks)

        # --------------------------------------------------
        # 7️⃣ Save Vectors
        # --------------------------------------------------
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Saving vectors",
            progress=90,
        )

        add_vectors(
            doc_id=doc_id,
            chunks=structured_chunks,
            embeddings=embeddings,
            user_id=user_id,
        )

        # --------------------------------------------------
        # 8️⃣ Mark Success
        # --------------------------------------------------
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.SUCCESS,
            message="Upload processed successfully",
            progress=100,
        )

        logger.info(
            "Upload complete | job_id=%s | doc_id=%s | user_id=%s",
            job_id,
            doc_id,
            user_id,
        )

    except Exception as e:
        logger.exception(
            "Upload failed | job_id=%s | user_id=%s | error=%s",
            job_id,
            user_id,
            str(e),
        )

        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.FAILED,
            message="Upload processing failed",
            error=str(e),
        )

        raise
