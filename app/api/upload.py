from fastapi import (
    APIRouter,
    UploadFile,
    File,
    BackgroundTasks,
    HTTPException,
    Depends,
    status,
)
from pathlib import Path
import shutil
import uuid
import os
import logging

from app.auth.dependencies import get_current_user
from app.core.config import UPLOAD_DIR
from app.core.jobs import create_job, process_upload
from app.core.job_types import JobType, JobStatus
from app.models.schemas import UploadJobResponse  # ✅ Correct model

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
MAX_SIZE_MB = 20


@router.post(
    "/",
    response_model=UploadJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    Upload a document and trigger background processing.
    """

    # ------------------------------------------------------
    # 1️⃣ Validate user
    # ------------------------------------------------------
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication context",
        )

    # ------------------------------------------------------
    # 2️⃣ Validate filename
    # ------------------------------------------------------
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    original_filename = os.path.basename(file.filename)
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {extension}",
        )

    # ------------------------------------------------------
    # 3️⃣ Validate file size
    # ------------------------------------------------------
    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine file size",
        )

    if size > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds maximum allowed size",
        )

    # ------------------------------------------------------
    # 4️⃣ Create job
    # ------------------------------------------------------
    job_id = create_job(JobType.UPLOAD, user_id)

    # ------------------------------------------------------
    # 5️⃣ Save file (user-isolated directory)
    # ------------------------------------------------------
    user_upload_dir = UPLOAD_DIR / user_id
    user_upload_dir.mkdir(parents=True, exist_ok=True)

    sanitized_filename = original_filename.replace(" ", "_")
    saved_filename = f"{uuid.uuid4()}_{sanitized_filename}"
    saved_path = user_upload_dir / saved_filename

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        logger.exception("File save failed | user=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file",
        )
    finally:
        await file.close()

    # ------------------------------------------------------
    # 6️⃣ Trigger background processing
    # ------------------------------------------------------
    background_tasks.add_task(
        process_upload,
        job_id,
        saved_path,
        sanitized_filename,
        user_id,
    )

    logger.info(
        "Upload accepted | user=%s | job_id=%s | filename=%s",
        user_id,
        job_id,
        saved_filename,
    )

    # ------------------------------------------------------
    # 7️⃣ Return job reference ONLY
    # ------------------------------------------------------
    return UploadJobResponse(
        job_id=job_id,
        status=JobStatus.RUNNING.value,
        filename=saved_filename
    )
