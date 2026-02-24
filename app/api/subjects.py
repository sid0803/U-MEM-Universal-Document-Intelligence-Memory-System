from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)

# ✅ Resolve absolute path safely
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUBJECTS_DIR = BASE_DIR / "data" / "subjects"


@router.get("/")
def list_subjects():
    # 1️⃣ Check directory exists
    if not SUBJECTS_DIR.exists():
        raise HTTPException(
            status_code=404,
            detail="Subjects directory not found"
        )

    # 2️⃣ Read folders safely
    try:
        subjects = sorted(
            folder.name
            for folder in SUBJECTS_DIR.iterdir()
            if folder.is_dir()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to read subjects directory"
        )

    # 3️⃣ Return clean response
    return {
        "count": len(subjects),
        "subjects": subjects
    }
