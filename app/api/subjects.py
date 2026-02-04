from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

SUBJECTS_DIR = Path("data/subjects")


@router.get("/subjects/")
def list_subjects():
    if not SUBJECTS_DIR.exists():
        return {"subjects": []}

    subjects = [
        folder.name
        for folder in SUBJECTS_DIR.iterdir()
        if folder.is_dir()
    ]

    return {
        "count": len(subjects),
        "subjects": subjects
    }
